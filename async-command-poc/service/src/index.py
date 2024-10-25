from aws_lambda_powertools.event_handler import Response, content_types
from aws_lambda_powertools.event_handler.exceptions import NotFoundError
from aws_lambda_powertools.utilities.typing import LambdaContext

from src.controller import account_controller, profile_controller
from src.log.logger import logger
from src.resolver.alb_resolver import app

app.include_router(profile_controller.router, prefix="/template/profiles")
app.include_router(account_controller.router, prefix="/template/accounts")


@logger.inject_lambda_context
def handle(event: dict, context: LambdaContext) -> dict | Exception:
    print(event)
    return app.resolve(event, context)


@app.not_found
def handle_not_found_errors(exc: NotFoundError) -> Response:
    logger.info(f"Not found route: {app.current_event.path}")
    return Response(
        status_code=418,
        content_type=content_types.TEXT_PLAIN,
        body=f"Not found route: {app.current_event.path}",
    )
