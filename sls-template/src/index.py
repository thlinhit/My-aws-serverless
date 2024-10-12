import json

from aws_lambda_powertools.utilities.typing import LambdaContext

from src.controller import profile_controller
from src.log.logger import logger
from src.resolver.alb_resolver import app

app.include_router(profile_controller.router, prefix="/template")

@logger.inject_lambda_context
def handle(event: dict, context: LambdaContext) -> dict | Exception:
    print(event)
    return app.resolve(event, context)
    # body = {
    #     "message": "Go Serverless v4.0! Your function executed successfully!",
    # }
    #
    # response = {"statusCode": 200, "body": json.dumps(body)}
    #
    # return response