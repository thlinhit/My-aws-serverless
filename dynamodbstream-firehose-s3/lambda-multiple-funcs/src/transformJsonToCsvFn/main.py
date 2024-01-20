import base64
import json

from aws_lambda_powertools import Logger
from aws_lambda_powertools.logging.formatters.datadog import DatadogLogFormatter

logger = Logger(logger_formatter=DatadogLogFormatter(), log_record_order=["level", "message", "location", "function_request_id"])

ENCODING = 'utf-8'

@logger.inject_lambda_context
def handler(event, context):
    records = []
    output = []
    logger.info(f"Received batch of {len(event['records'])} records")

    for record in event['records']:
        payload = json.loads(base64.b64decode(record['data']).decode(ENCODING))
        logger.info(f"data: {payload}")
        output.append({
            'recordId': record['recordId'],
            'result': 'Ok',
            'data': base64.b64encode(dict(payload).encode(ENCODING)).decode(ENCODING)
        })

    return {'records': output}