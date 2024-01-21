import base64
import json
import datetime
from aws_lambda_powertools import Logger
from aws_lambda_powertools.logging.formatters.datadog import DatadogLogFormatter

logger = Logger(logger_formatter=DatadogLogFormatter(), log_record_order=["level", "message", "location", "function_request_id"])

ENCODING = 'utf-8'

@logger.inject_lambda_context
def handler(event, context):

    output = []
    logger.info(f"Received batch of {len(event['records'])} records")
    logger.info(f"{event}")

    headers = ['product_code', 'identity_id', 'identity_type', 'transaction_id', 'transaction_date', 'transaction_amount']
    header_included = False

    partition_keys = {"bankname": 'BANK_NAME',
                      "product": "MCA",
                      "partner": "PARTNER_NAME",
                      "date": datetime.date.today().strftime("%Y%m%d")
                      }

    for record in event['records']:
        payload = convert_to_json(record['data'])
        row_fields = [payload.get(field, '') for field in headers]
        row_str = ",".join(row_fields)
        data = (row_str if header_included is True else ",".join(headers) + "\n" + row_str)
        output.append(
            {
                'recordId': record['recordId'],
                'result': 'Ok',
                'data': base64.b64encode((data + "\n").encode(ENCODING)),
                'metadata': {'partitionKeys': partition_keys}
            }
        )

    return {'records': output}

def convert_to_json(encoded_base64_data) -> object:
    return json.loads(base64.b64decode(encoded_base64_data).decode(ENCODING))