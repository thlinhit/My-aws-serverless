import os
from datetime import datetime

import boto3
from boto3.dynamodb.conditions import Attr, ConditionBase
from botocore.config import Config as BotoCfg
from botocore.exceptions import ClientError

from src.shared.dynamodb import dynamodb_helper
from src.shared.exception.domain_code import DomainCode
from src.shared.exception.domain_error import DomainError
from src.shared.log.logger import logger

DYNAMO_DB_SERVICE = "dynamodb"
DEFAULT_REGION = os.environ["DEFAULT_REGION"]

dynamodb_client = boto3.resource(DYNAMO_DB_SERVICE, region_name=DEFAULT_REGION, config=BotoCfg(retries={"mode": "standard"}))

_DYNAMODB_CONFIG = {}

DATETIME_FORMAT = "%m/%d/%YT%H:%M:%S"


def get_table(table_name: str):
    if table_name not in _DYNAMODB_CONFIG:
        _DYNAMODB_CONFIG[table_name] = dynamodb_client.Table(table_name)
    return _DYNAMODB_CONFIG[table_name]


def put_item_if_not_exists(table_name, item):
    logger.debug("put item in table: {}, item: {}".format(table_name, item))
    try:
        table = get_table(table_name)
        response = table.put_item(
            Item={"modified_date": int(datetime.utcnow().timestamp()), "iso_created_date": datetime.utcnow().strftime(DATETIME_FORMAT), **item},
            ConditionExpression=Attr("sk").not_exists(),
        )
        return response
    except ClientError as client_error:
        if client_error.response["Error"]["Code"] == "ConditionalCheckFailedException":
            raise DomainError(DomainCode.DYNAMODB_CONDITIONAL_CHECK_FAILED_ERROR, table_name, item["pk"], item["sk"])
        else:
            raise DomainError(DomainCode.DYNAMODB_ERROR, table_name, item["pk"], item["sk"], str(client_error))
    except Exception as ex:
        raise DomainError(DomainCode.DYNAMODB_ERROR, table_name, item["pk"], item["sk"], str(ex))


def put_item_conditionally(table_name, item, condition: ConditionBase):
    logger.debug("put item in table: {}, item: {}".format(table_name, item))
    try:
        table = get_table(table_name)
        response = table.put_item(
            Item={"modified_date": int(datetime.utcnow().timestamp()), "iso_created_date": datetime.utcnow().strftime(DATETIME_FORMAT), **item},
            ConditionExpression=condition,
        )
        return response
    except ClientError as client_error:
        if client_error.response["Error"]["Code"] == "ConditionalCheckFailedException":
            raise DomainError(DomainCode.DYNAMODB_CONDITIONAL_CHECK_FAILED_ERROR, table_name, item["pk"], item["sk"])
        else:
            raise DomainError(DomainCode.DYNAMODB_ERROR, table_name, item["pk"], item["sk"], str(client_error))
    except Exception as ex:
        raise DomainError(DomainCode.DYNAMODB_ERROR, table_name, item["pk"], item["sk"], str(ex))


def find_item(table_name, pk: str, sk: str):
    logger.info("Find item in table: {}, pk: {}, sk: {}".format(table_name, pk, sk))
    try:
        table = get_table(table_name)
        response = table.get_item(Key={"pk": pk, "sk": sk})
        is_present = True if "Item" in response else False
        item = response["Item"] if "Item" in response else None
        return is_present, item
    except Exception as ex:
        raise DomainError(DomainCode.DYNAMODB_ERROR, table_name, pk, sk, str(ex))


def find_by_sort_key_prefix(table_name, pk: str, sk_prefix: str) -> list:
    logger.info("Find items in table: {}, pk: {}, sk_prefix: {}".format(table_name, pk, sk_prefix))
    try:
        table = get_table(table_name)
        response = table.query(
            KeyConditionExpression="pk = :pk AND begins_with(sk, :sk_prefix)",
            ExpressionAttributeValues={":pk": pk, ":sk_prefix": sk_prefix},
        )
        items = response["Items"] if "Items" in response else []
        logger.info("Found {} items in table: {}, pk: {}, sk_prefix: {}".format(len(items), table_name, pk, sk_prefix))
        return list(map(dynamodb_helper.convert_to_python_obj, items))
    except Exception as ex:
        raise DomainError(DomainCode.DYNAMODB_ERROR, table_name, pk, sk_prefix, str(ex))


def find_latest_by_sort_key_prefix(table_name, pk: str, sk_prefix: str):
    logger.info("Find latest item in table: {}, pk: {}, sk_prefix: {}".format(table_name, pk, sk_prefix))
    try:
        table = get_table(table_name)
        response = table.query(
            KeyConditionExpression="pk = :pk AND begins_with(sk, :sk_prefix)",
            ExpressionAttributeValues={":pk": pk, ":sk_prefix": sk_prefix},
            ScanIndexForward=False,
            Limit=1,
        )
        is_present = True if "Items" in response else False
        item = dynamodb_helper.convert_to_python_obj(response["Items"][0]) if "Items" in response and len(response["Items"]) > 0 else None
        return is_present, item
    except Exception as ex:
        raise DomainError(DomainCode.DYNAMODB_ERROR, table_name, pk, sk_prefix, str(ex))
