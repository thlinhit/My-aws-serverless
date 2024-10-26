import os
from typing import Optional

import boto3
from boto3.dynamodb.conditions import AttributeBase
from botocore.config import Config as BotoCfg
from botocore.exceptions import ClientError

from src.exception.domain_code import DomainCode
from src.exception.domain_exception import DomainException
from src.log.logger import logger
from src.repository.model import Item
from src.repository.model.key import Key
from src.repository.model.update_behavior import UpdateBehavior
from src.util import datetime_util

DYNAMO_DB_SERVICE = "dynamodb"
REGION = os.environ["REGION"]
TABLE_REGION = os.getenv("TABLE_REGION", REGION)

IS_LOCAL = os.environ.get("RUNNING_STAGE", "local") == "local"
if IS_LOCAL:
    dynamodb_client = boto3.resource(
        DYNAMO_DB_SERVICE,
        endpoint_url="http://localhost:8000",
        region_name="localhost",
        aws_access_key_id='dummy',
        aws_secret_access_key='dummy',
    )
else:
    dynamodb_client = boto3.resource(
        DYNAMO_DB_SERVICE,
        region_name=TABLE_REGION,
        config=BotoCfg(retries={"mode": "standard"}),
    )

_DYNAMODB_CONFIG = {}


def get_table(table_name: str):
    if table_name not in _DYNAMODB_CONFIG:
        _DYNAMODB_CONFIG[table_name] = dynamodb_client.Table(table_name)
    return _DYNAMODB_CONFIG[table_name]


def get_item(table_name: str, key: Key) -> dict:
    is_present, item = find_item(table_name, key)
    if not is_present:
        raise DomainException(DomainCode.ITEM_NOT_FOUND, table_name, key.pk, key.sk)
    return item


def find_item(table_name, key: Key) -> tuple[bool, dict | None]:
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
        raise DomainException(
            DomainCode.DYNAMODB_ERROR, table_name, repr(ex)
        )


def update_item(
        table_name: str,
        item: Item,
        condition_expression: AttributeBase = None,
        ignore_none_fields: bool = False
) -> Optional[dict]:
    item_key: Key = item.get_key()
    try:

        update_data = item.model_dump(by_alias=True, exclude=["pk", "sk"], exclude_none=ignore_none_fields)

        if not update_data:
            logger.info(f"Nothing to update, table={table_name}, key={item_key}")
            return

        update_data["updatedAt"] = datetime_util.utc_iso_now()

        update_expressions = []
        expression_attribute_values = {}

        for field_name, field in item.model_fields.items():
            field_metadata = (field.json_schema_extra or {}).get('metadata', {})
            alias = field.alias or field_name
            if alias not in update_data:
                continue

            if field_metadata.get(UpdateBehavior.KEY, None) == UpdateBehavior.WRITE_IF_NOT_EXIST.value:
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
            raise DomainException(
                DomainCode.DYNAMODB_CONDITIONAL_CHECK_FAILED_ERROR,
                table_name,
                item_key.pk,
                item_key.sk,
            )
        else:
            raise DomainException(
                DomainCode.DYNAMODB_ERROR,
                table_name,
                item_key.pk,
                item_key.sk,
                repr(client_error),
            )
    except Exception as ex:
        raise DomainException(
            DomainCode.DYNAMODB_ERROR, table_name, repr(ex)
        )
