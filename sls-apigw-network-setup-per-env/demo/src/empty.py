import json
from typing import Dict, Union


def handler(event, context):
    """
    Empty handler function. Not actually called as we're using HTTP proxy integration.
    """
    return response({
       "message": "Response from lambda proxy!"
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
