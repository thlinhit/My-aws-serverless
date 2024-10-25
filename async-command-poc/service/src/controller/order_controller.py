import http
import json
from decimal import Decimal
from types import SimpleNamespace

from aws_lambda_powertools.event_handler import Response, content_types
from aws_lambda_powertools.event_handler.router import ALBRouter

from src.log.logger import logger
router = ALBRouter()

@router.post("/orders")
def place_order():
    logger.info(f"Request received to create an order")
    event = router.current_event.json_body
    logger.info(f"event {event}")
    payload = json.loads(router.current_event.body, object_hook=lambda d: SimpleNamespace(**d), parse_float=Decimal)

    return Response(
        status_code=http.HTTPStatus.ACCEPTED,
        body=event,
        content_type=content_types.APPLICATION_JSON
    )