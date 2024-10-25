from aws_lambda_powertools.event_handler import Response, content_types
from aws_lambda_powertools.event_handler.exceptions import NotFoundError
from aws_lambda_powertools.utilities.typing import LambdaContext

from src.controller import order_controller
from src.log.logger import logger
from src.resolver.apigw_resolver import app


app.include_router(order_controller.router, prefix="/ecommerce/orders")


@logger.inject_lambda_context
def handle(event: dict, context: LambdaContext) -> dict | Exception:
    logger.info(app.__dict__)
    return app.resolve(event, context)


@app.not_found
def handle_not_found_errors(_exc: NotFoundError) -> Response:
    logger.info(f"Not found route: {app.current_event.path}")
    return Response(
        status_code=418,
        content_type=content_types.TEXT_PLAIN,
        body=f"Not found route: {app.current_event.path}",
    )
