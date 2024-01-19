import os

import boto3
from botocore.exceptions import ClientError

from src.shared.exception.domain_code import DomainCode
from src.shared.exception.domain_error import DomainError
from src.shared.log.logger import logger
from src.shared.model import sqs_message

sqs_client = boto3.client("sqs")

sqs_resource = None

_SQS_CONFIG = {"sqsResource": None, "dlq": None}

DEFAULT_REGION = os.environ["DEFAULT_REGION"]


def get_queue(queue_name: str):
    if _SQS_CONFIG["sqsResource"] is None:
        _SQS_CONFIG["sqsResource"] = boto3.resource("sqs", region_name=DEFAULT_REGION)

    if queue_name not in _SQS_CONFIG:
        _SQS_CONFIG[queue_name] = _SQS_CONFIG["sqsResource"].get_queue_by_name(QueueName=queue_name)

    return _SQS_CONFIG[queue_name]


def send_message(queue_name: str, message: str):
    try:
        queue = get_queue(queue_name)
        queue.send_message(MessageBody=message)
    except ClientError as client_error:
        raise DomainError(DomainCode.SQS_SEND_ERROR, queue_name, message, client_error)


def change_message_visibility(queue_url, next_interval, record, transaction_key):
    try:
        logger.info(f"Start change message visibility, transactionKey:{transaction_key}, nextInterval:{next_interval}")
        sqs_client.change_message_visibility(
            QueueUrl=queue_url,
            ReceiptHandle=record["receiptHandle"],
            VisibilityTimeout=next_interval,
        )
        raise DomainError(DomainCode.SQS_RETRY_NEXT_TIME, next_interval, transaction_key)
    except Exception as e:
        if not isinstance(e, DomainError):
            logger.exception(e)
            raise DomainError(
                DomainCode.SQS_CHANGE_VISIBILITY_ERROR,
                transaction_key,
                queue_url,
                repr(e),
            )
        else:
            raise e


def send_to_dlq(ifm_dql_name, function_name, domain_code, e, record):
    try:
        send_message(
            ifm_dql_name,
            sqs_message.build_dlq_message(
                function_name=function_name,
                exception=DomainError(domain_code, e.message),
                payload=record,
                original_error_message=str(e),
            ),
        )
    except DomainError as e:
        logger.error(e)
        if e.domain_code == DomainCode.UNKNOWN:
            return
        else:
            raise e
