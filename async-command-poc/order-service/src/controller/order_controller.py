import http

from aws_lambda_powertools.event_handler import Response, content_types
from aws_lambda_powertools.event_handler.router import APIGatewayHttpRouter
from aws_lambda_powertools.utilities.validation import validate, SchemaValidationError

from src.controller.dto.place_order_dto import PlaceOrderDto
from src.exception.domain_code import DomainCode
from src.exception.domain_error import DomainError
from src.log.logger import logger
from src.service import order_service
from src.util import file_util

router = APIGatewayHttpRouter()


@router.post("")
def place_order():
    logger.info(f"Request received to create an order")
    try:
        payload = router.current_event.json_body

        validate(event=payload, schema=file_util.load_json_schema('create_order_request_schema.json'))

        place_order_dto = PlaceOrderDto.model_validate(payload)

        order_service.create_order(order=place_order_dto.to_domain())

        return Response(
            status_code=http.HTTPStatus.ACCEPTED,
            body=place_order_dto.to_domain(),
            content_type=content_types.APPLICATION_JSON,
        )
    except SchemaValidationError as e:
        raise DomainError(DomainCode.VALIDATION_ERROR, str(e))
