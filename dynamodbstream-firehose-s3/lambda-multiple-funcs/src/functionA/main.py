import os
import uuid

from src.shared.repository.dynamodb_repository import put_item

DYNAMO_DB_TABLE = os.environ["DYNAMO_DB_TABLE"]
def handler(event, context):
    put_item(DYNAMO_DB_TABLE, {
        "PK": "TESTPK",
        "SK": str(uuid.uuid4()),
        "testKey1": "testValue1"
    })