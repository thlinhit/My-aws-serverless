import os
from typing import Optional, List

import boto3
from boto3.dynamodb.conditions import AttributeBase, Key
from botocore.config import Config as BotoCfg
from botocore.exceptions import ClientError
from tenacity import retry, stop_after_attempt, retry_if_exception_type, wait_exponential_jitter

from src.config.env import REGION
from src.exception.domain_code import DomainCode
from src.exception.domain_error import DomainError
from src.log.logger import logger
from src.repository.model.item import Item
from src.repository.model.key import ItemKey
from src.repository.model.update_behavior import UpdateBehavior
from src.util import datetime_util

DYNAMO_DB_SERVICE = "dynamodb"

IS_LOCAL = os.environ.get("RUNNING_STAGE", "local") == "local"
if IS_LOCAL:
    dynamodb_resource = boto3.resource(
        DYNAMO_DB_SERVICE,
        endpoint_url="http://localhost:8000",
        region_name="localhost",
        aws_access_key_id="dummy",
        aws_secret_access_key="dummy",
    )
else:
    dynamodb_resource = boto3.resource(
        DYNAMO_DB_SERVICE,
        region_name=REGION,
        config=BotoCfg(retries={"mode": "standard"}),
    )

_DYNAMODB_CONFIG = {}


def _get_dynamodb_client():
    return dynamodb_resource.meta.client


def get_table(table_name: str):
    if table_name not in _DYNAMODB_CONFIG:
        _DYNAMODB_CONFIG[table_name] = dynamodb_resource.Table(table_name)
    return _DYNAMODB_CONFIG[table_name]


def get_item(table_name: str, key: ItemKey) -> dict:
    is_present, item = find_item(table_name, key)
    if not is_present:
        raise DomainError(DomainCode.ITEM_NOT_FOUND, table_name, key.pk, key.sk)
    return item


def find_item(table_name, key: ItemKey) -> tuple[bool, dict | None]:
    logger.info(
        "Find item in table: {}, pk: {}, sk: {}".format(table_name, key.pk, key.sk)
    )
    try:
        table = get_table(table_name)
        response = table.get_item(Key=key.model_dump())
        is_present = True if "Item" in response else False
        item = response["Item"] if "Item" in response else None
        return is_present, item
    except Exception as ex:
        raise DomainError(DomainCode.DYNAMODB_ERROR, table_name, repr(ex))


def get_items_by_pk(table_name: str, pk: str) -> list:
    try:
        response = _get_dynamodb_client().query(
            TableName=table_name,
            KeyConditionExpression=Key('pk').eq(pk)
        )
        return response.get('Items', [])
    except Exception as ex:
        raise DomainError(DomainCode.DYNAMODB_ERROR, table_name, repr(ex))


def update_item(
        table_name: str,
        item: Item,
        condition_expression: AttributeBase = None,
        ignore_none_fields: bool = False,
) -> Optional[dict]:
    item_key: ItemKey = item.get_key()
    try:

        update_data = item.model_dump(
            by_alias=True, exclude={"pk", "sk"}, exclude_none=ignore_none_fields
        )

        if not update_data:
            logger.info(f"Nothing to update, table={table_name}, key={item_key}")
            return

        update_data["updatedAt"] = datetime_util.utc_iso_now()

        update_expressions = []
        expression_attribute_values = {}

        for field_name, field in item.model_fields.items():
            field_metadata = (field.json_schema_extra or {}).get("metadata", {})
            alias = field.alias or field_name
            if alias not in update_data:
                continue

            if (
                    field_metadata.get(UpdateBehavior.KEY, None)
                    == UpdateBehavior.WRITE_IF_NOT_EXIST.value
            ):
                update_expressions.append(f"{alias} = if_not_exists({alias}, :{alias})")
            else:
                update_expressions.append(f"{alias} = :{alias}")

            expression_attribute_values[f":{alias}"] = update_data[alias]

        update_expression = "SET " + ", ".join(update_expressions)

        update_kwargs = {
            "Key": item_key.model_dump(by_alias=True),
            "UpdateExpression": update_expression,
            "ExpressionAttributeValues": expression_attribute_values,
            "ReturnValues": "ALL_NEW",
        }
        if condition_expression:
            update_kwargs["ConditionExpression"] = condition_expression

        return get_table(table_name).update_item(**update_kwargs)["Attributes"]
    except ClientError as client_error:
        if client_error.response["Error"]["Code"] == "ConditionalCheckFailedException":
            raise DomainError(
                DomainCode.DYNAMODB_CONDITIONAL_CHECK_FAILED_ERROR,
                table_name,
                item_key.pk,
                item_key.sk,
            )
        else:
            raise DomainError(
                DomainCode.DYNAMODB_ERROR,
                table_name,
                item_key.pk,
                item_key.sk,
                repr(client_error),
            )
    except Exception as ex:
        raise DomainError(DomainCode.DYNAMODB_ERROR, table_name, repr(ex))


def batch_get_items(table_name: str, keys: list[ItemKey]) -> list[dict]:
    logger.info(f"Batch get items from table: {table_name}")
    all_items = []
    keys_list = [key.model_dump() for key in keys]

    for i in range(0, len(keys_list), 20):
        batch_keys = keys_list[i:i + 20]
        request_items = {table_name: {"Keys": batch_keys}}

        while request_items:
            try:
                response = _get_items(request_items)
                items = response.get("Responses", {}).get(table_name, [])
                all_items.extend(items)
                unprocessed_keys = response.get("UnprocessedKeys", {})
                if not unprocessed_keys:
                    break
                request_items = unprocessed_keys
                logger.warning("Retrying unprocessed keys...")
            except ClientError as client_error:
                logger.error(f"Client error while fetching items: {client_error}")
                raise DomainError(
                    DomainCode.DYNAMODB_ERROR,
                    table_name,
                    repr(client_error)
                )
            except Exception as ex:
                logger.error(f"Unexpected error: {ex}")
                raise DomainError(DomainCode.DYNAMODB_ERROR, table_name, repr(ex))

    return all_items


@retry(
    retry=retry_if_exception_type(ClientError),
    wait=wait_exponential_jitter(max=5),
    stop=stop_after_attempt(3)
)
def _get_items(request_items: List[dict]):
    return _get_dynamodb_client().batch_get_item(RequestItems=request_items)


class DynamoDBTransactionHelper:
    def __init__(self, table_name):
        self.table_name = table_name
        self.transact_items = []

    def add_put_item(self, item: Item, condition_expression: str = None):
        put_kwargs = {
            "TableName": self.table_name,
            "Item": item.model_dump(by_alias=True),
        }
        if condition_expression:
            put_kwargs["ConditionExpression"] = condition_expression
        self.transact_items.append({"Put": put_kwargs})

    def add_update_item(self, key, update_expr, expr_attr_values):
        pass

    def execute_transaction(self):
        try:
            response = dynamodb_resource.meta.client.transact_write_items(
                TransactItems=self.transact_items
            )
            logger.info("Transaction successful: ", response)
        except ClientError as client_error:
            if client_error.response["Error"]["Code"] == "TransactionCanceledException":
                reasons = client_error.response.get("CancellationReasons", [])
                for reason in reasons:
                    if reason["Code"] == "ConditionalCheckFailed":
                        raise DomainError(
                            DomainCode.DYNAMODB_CONDITIONAL_CHECK_FAILED_ERROR,
                            self.table_name,
                        )

            raise DomainError(
                DomainCode.DYNAMODB_ERROR,
                self.table_name,
                repr(client_error),
            )
        except Exception as ex:
            raise DomainError(
                DomainCode.DYNAMODB_ERROR,
                self.table_name,
                repr(ex),
            )
