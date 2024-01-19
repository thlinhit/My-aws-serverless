import boto3
from botocore.config import Config as BotoCfg

from src.exception.domain_code import DomainCode
from src.exception.domain_exception import DomainException
import os

DYNAMO_DB_SERVICE = "dynamodb"
DEFAULT_REGION = os.environ["LOAN_ACCOUNT_TABLE_REGION"]

dynamodb_client = boto3.resource(DYNAMO_DB_SERVICE, region_name=DEFAULT_REGION,
                                 config=BotoCfg(retries={"mode": "standard"}))

_DYNAMODB_CONFIG = {}


def get_table(table_name: str):
    if table_name not in _DYNAMODB_CONFIG:
        _DYNAMODB_CONFIG[table_name] = dynamodb_client.Table(table_name)
    return _DYNAMODB_CONFIG[table_name]


def find_item(table_name, pk: str, sk: str):
    try:
        table = get_table(table_name)
        response = table.get_item(Key={"PK": pk, "SK": sk})
        is_present = True if "Item" in response else False
        item = response["Item"] if "Item" in response else None
        return is_present, item
    except Exception:
        raise DomainException(DomainCode.DYNAMODB_ITEM_NOT_FOUND)
