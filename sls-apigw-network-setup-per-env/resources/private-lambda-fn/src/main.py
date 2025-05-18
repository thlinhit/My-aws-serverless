import json
from typing import Union, Dict

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()


@logger.inject_lambda_context
def handler(event, context: LambdaContext):
    logger.info(f"Received transaction event: {event}")
    return response({
        "message": "Transaction received!"
    })


def response(
        msg: Union[dict, str],
        status_code: int = 200,
        allow_origin: str = "*",
        allow_headers: str = "Content-Type,X-Amz-Date,Authorization,X-Api-Key,x-requested-with",
        allow_methods: str = "POST"
) -> Dict[str, Union[int, str]]:
    if isinstance(msg, str):
        msg = {"message": msg}
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Headers": allow_headers,
            "Access-Control-Allow-Origin": allow_origin,
            "Access-Control-Allow-Methods": allow_methods,
            "content-type": "application/json; charset=utf-8"
        },
        "body": json.dumps(msg, ensure_ascii=False)
    }
