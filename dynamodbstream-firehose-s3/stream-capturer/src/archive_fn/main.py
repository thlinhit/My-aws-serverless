import os

from aws_lambda_powertools.utilities.data_classes.dynamo_db_stream_event import (
    StreamRecord,
)
from aws_lambda_powertools.utilities.typing import LambdaContext

from ..shared.exception.domain_code import DomainCode
from ..shared.exception.domain_error import DomainError
from ..shared.log.logger import logger
from ..shared.model import sqs_message
from ..shared.sqs import sqs_service
from . import data_accumulator
from .firehose_client import put_records

FIREHOSE_RECORD_MINIMAL_SIZE: int = os.getenv("FIREHOSE_RECORD_MINIMAL_SIZE", 5000)
DQL_NAME = os.getenv("DQL_NAME", "test-dlq-sqs")
FUNCTION_NAME = os.environ["POWERTOOLS_SERVICE_NAME"]


@logger.inject_lambda_context
def handler(event, context: LambdaContext):
    logger.info(f"Start processing {len(event['Records'])} records")
    logger.debug(event)

    try:
        data: str = data_accumulator.accumulate(event["Records"])
        # Remove transactionKey as following logs are not related to one single transaction
        logger.remove_keys(["transactionKey"])
        logger.info(f"Completed at accumulating items, size: {len(data.encode('utf-8'))} bytes")

        if len(data) > 0:
            put_records([{"Data": data}])
        else:
            logger.info("Do nothing as accumulated data is empty")
    except Exception as exception:
        handle_error(exception, context, event["Records"])


def handle_error(exception: Exception, context: LambdaContext, records: list[StreamRecord]):
    if isinstance(exception, DomainError):
        if exception.domain_code == DomainCode.FIREHOSE_PUT_ERROR:
            logger.info("Encountered an issue while putting data into Firehose, will retry...")
            raise exception
    logger.exception(exception)
    sqs_service.send_message(
        IFM_DLQ_NAME,
        sqs_message.build_dlq_message(function_name=FUNCTION_NAME, exception=exception, aws_request_id=context.aws_request_id, records=records),
    )
