import os
from typing import Dict, Union

from aws_lambda_powertools.utilities.data_classes.dynamo_db_stream_event import (
    StreamRecord,
)

from src.shared.dynamodb import dynamodb_helper
from src.shared.exception.domain_code import DomainCode
from src.shared.exception.domain_error import DomainError
from src.shared.log.logger import logger
from src.shared.model import sqs_message
from src.shared.sqs import sqs_service
from src.shared.utils import dict_util, json_util, string_util

IFM_DLQ_NAME = os.getenv("IFM_DLQ_NAME", "tp-actimize-ifm-dlq")
FUNCTION_NAME = os.environ["POWERTOOLS_SERVICE_NAME"]


def accumulate(records: list[StreamRecord]) -> str:
    result = ""
    for record in records:
        try:
            validate(record)
            payload = extract(record)
            result += payload["item"]
            logger.info("successfully append record data into batch")
        except Exception as exception:
            error_message = str(exception)
            record_id = record["eventID"]
            logger.error({"errorMessage": error_message, "recordId": record_id})
            send_to_dlq(exception, record)
    return result


def send_to_dlq(exception: Exception, record: StreamRecord):
    sqs_service.send_message(IFM_DLQ_NAME, sqs_message.build_dlq_message(function_name=FUNCTION_NAME, exception=exception, record=record))


def validate(record: StreamRecord):
    if not dict_util.key_exists(record, ["dynamodb", "Keys", "PK", "S"]) or string_util.is_blank(record["dynamodb"]["Keys"]["PK"]["S"]):
        raise DomainError(DomainCode.VALIDATION_ERROR, "The record does not have a key")

    if not dict_util.key_exists(record, ["dynamodb", "OldImage"]):
        raise DomainError(DomainCode.VALIDATION_ERROR, "The record does not have OldImage")


def extract(record: StreamRecord) -> Dict[str, Union[str, str]]:
    dynamodb_payload = record["dynamodb"]
    partition_key = str(dynamodb_payload["Keys"]["PK"]["S"])

    transaction_key = None

    if partition_key.startswith("TXN#"):
        transaction_key = partition_key.replace("TXN#", "")
        logger.append_keys(transactionKey=transaction_key)
    else:
        logger.warning(
            {
                "description": "item does not belong to a transaction",
                "pk": partition_key,
                "sk": dynamodb_payload["Keys"]["SK"]["S"] if dict_util.key_exists(dynamodb_payload, ["Keys", "SK", "S"]) else None,
            }
        )

    item: str = json_util.dumps_and_appends_new_line(dynamodb_helper.convert_to_python_obj(record["dynamodb"]["OldImage"]))

    return {"transactionKey": transaction_key, "item": item}
