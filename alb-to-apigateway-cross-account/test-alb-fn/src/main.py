import os

from aws_lambda_powertools.logging.logger import logger
from aws_lambda_powertools.utilities.typing import LambdaContext


@logger.inject_lambda_context
def handler(event, context: LambdaContext):
    logger.info(f"Start processing {len(event['Records'])} records")
    logger.debug(event)
