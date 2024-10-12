import http

from aws_lambda_powertools.event_handler import Response, content_types
from aws_lambda_powertools.event_handler.router import ALBRouter

from src.dto.account import Account
from src.log.logger import logger
from src.repository import account_repository

router = ALBRouter()


@router.get("/<account_number>")
def get_account(account_number: str):
    logger.debug(f"Getting account info, account_number {account_number}")

    account: Account = account_repository.get_account(account_number)

    return Response(
        status_code=http.HTTPStatus.OK,
        body=account,
        content_type=content_types.APPLICATION_JSON,
    )
