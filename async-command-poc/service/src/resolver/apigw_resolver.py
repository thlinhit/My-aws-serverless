import http

from aws_lambda_powertools.event_handler import (APIGatewayHttpResolver, Response,
                                                 content_types)

from src.exception.domain_exception import DomainException
from src.log.logger import logger

app = APIGatewayHttpResolver()


@app.exception_handler(ValueError)
def handle_value_error(error: ValueError) -> Response:
    logger.error(error)
    return Response(
        http.HTTPStatus.BAD_REQUEST,
        content_type=content_types.TEXT_PLAIN,
        body="Invalid parameters",
    )


@app.exception_handler(DomainException)
def handle_domain_exception(ex: DomainException):
    logger.exception(ex)
    http_status = http.HTTPStatus.INTERNAL_SERVER_ERROR
    return Response(
        status_code=http_status.value,
        body={
            "errors": [
                {
                    "errorCode": f"{ex.domain_code.external_code}",
                    "errorMessage": f"{ex.internal_message}",
                }
            ]
        },
        content_type=content_types.APPLICATION_JSON,
    )
