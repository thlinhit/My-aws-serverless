import os
import json
import boto3

from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Logger

logger = Logger()

PARTNER_NAME = os.getenv("PARTNER_NAME", "PAYMONGO")
alb_egress_domain = os.getenv("ALB_DOMAIN", "")

client = boto3.client('stepfunctions')


@logger.inject_lambda_context
@event_source(data_class=SQSEvent)
def handle(event: SQSEvent, _: LambdaContext):
    for record in event.records:
        logger.info(f"Received triggering record: {record}")
        body = json.loads(record.body)
        logger.info(f"Body event: {body}")
        task_token = body['TaskToken']
        client.send_task_success(
            taskToken=task_token,
            output=json.dumps({
               'entityId': '9fff7495-cf46-40d1-91c3-d8791a4507ab'
            })
        )




