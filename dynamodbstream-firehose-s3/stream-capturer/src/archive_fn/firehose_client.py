import os
from typing import Dict

import boto3

from src.shared.exception.domain_code import DomainCode
from src.shared.exception.domain_error import DomainError
from src.shared.log.logger import logger

firehose_client = boto3.client("firehose")
STREAM_NAME = os.environ["FIREHOSE_STREAM_NAME"]


def put_records(records: list[Dict[str, str]]):
    logger.info(f"Sending {len(records)} record FireHose...")
    response = firehose_client.put_record_batch(DeliveryStreamName=STREAM_NAME, Records=records)
    logger.debug(response)
    if response["FailedPutCount"] > 0:
        raise DomainError(DomainCode.FIREHOSE_PUT_ERROR)
    else:
        logger.info("Successfully put records into Firehose")
