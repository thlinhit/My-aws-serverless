import os

import boto3
from botocore.exceptions import ClientError

from src.shared.exception.domain_code import DomainCode
from src.shared.exception.domain_error import DomainError

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
