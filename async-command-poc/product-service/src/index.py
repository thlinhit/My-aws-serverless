import http

from aws_lambda_powertools.event_handler import Response, content_types
from aws_lambda_powertools.event_handler.exceptions import NotFoundError
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.validation import SchemaValidationError

from src.controller import product_controller
from src.exception.domain_error import DomainError
from src.log.logger import logger
from src.resolver.apigw_resolver import app

app.include_router(product_controller.router, prefix="/ecommerce/products")


@logger.inject_lambda_context
def handle(event: dict, context: LambdaContext) -> dict | Exception:
    return app.resolve(event, context)


@app.not_found
def handle_not_found_errors(_exc: NotFoundError) -> Response:
    logger.info(f"Not found route: {app.current_event.path}")
    return Response(
        status_code=418,
        content_type=content_types.TEXT_PLAIN,
        body=f"Not found route: {app.current_event.path}",
    )

@app.exception_handler(DomainError)
def handle_domain_errors(domain_error: DomainError) -> Response:
    logger.exception(domain_error)
    return Response(
        status_code=http.HTTPStatus.BAD_REQUEST,
        content_type=content_types.APPLICATION_JSON,
        body={
            "error": domain_error.domain_code.external_code,
            "message": domain_error.internal_message,
        },
    )



@app.exception_handler(SchemaValidationError)
def handle_schema_validation_error(ex: SchemaValidationError):
    logger.exception(ex)
    return Response(
        status_code=http.HTTPStatus.BAD_REQUEST,
        content_type=content_types.TEXT_PLAIN,
        body=str(ex),
    )
