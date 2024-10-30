import http

from aws_lambda_powertools.event_handler import Response, content_types
from aws_lambda_powertools.event_handler.router import APIGatewayHttpRouter
from aws_lambda_powertools.utilities.validation import validate, SchemaValidationError

from src.exception.domain_code import DomainCode
from src.exception.domain_error import DomainError
from src.log.logger import logger
from src.util import file_util

router = APIGatewayHttpRouter()


@router.post("/validate")
def validate_product():
    try:
        logger.info(f"Request received to validate products")
        payload = router.current_event.json_body

        validate(event=payload, schema=file_util.load_json_schema('validate_products_schema.v1.json'))

        logger.info(f"Validate if the products have adequate stock to meet requirements....")
        # do something
        logger.info(f"It seems all goods are available....")

        return Response(
            status_code=http.HTTPStatus.OK,
            body={
                "products": []
            },
            content_type=content_types.APPLICATION_JSON,
        )
    except SchemaValidationError as e:
        raise DomainError(DomainCode.VALIDATION_ERROR, str(e))
