import json
import os

from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from aws_lambda_powertools.utilities.typing import LambdaContext

from src.exception.domain_code import DomainCode
from src.exception.domain_error import DomainError
from src.log.logger import logger

PARTNER_NAME = os.getenv("PARTNER_NAME", "PAYMONGO")
alb_egress_domain = os.getenv("ALB_DOMAIN", "")


@logger.inject_lambda_context
@event_source(data_class=SQSEvent)
def handle(event: SQSEvent, _: LambdaContext):
    for record in event.records:
        try:
            logger.info(f"Received triggering record: {record}")
            body = json.loads(record.body)
            logger.info(f"Body event: {body}")
        except DomainError as e:
            raise e
        except Exception as e:
            raise DomainError(DomainCode.UNKNOWN, str(e))
