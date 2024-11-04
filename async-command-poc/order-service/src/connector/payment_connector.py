import os
from urllib.parse import urlparse

import requests
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter

from src.config import aws_ssm_config
from src.config.env import REGION
from src.connector.retryable_http_error import RetryableHTTPError
from src.domain.order import Order
from src.exception.domain_code import DomainCode
from src.exception.domain_error import DomainError
from src.log.logger import logger

# The payment URL should be set as a parameter. I added it to SSM for demonstration convenience.
PAYMENT_URL_SSM = os.getenv("PAYMENT_URL_SSM")


@retry(
    retry=retry_if_exception_type(RetryableHTTPError),
    wait=wait_exponential_jitter(max=10),
    stop=stop_after_attempt(3)
)
def validate(order: Order) -> bool:
    try:
        payment_url: str = aws_ssm_config.get(PAYMENT_URL_SSM, max_age=900)
        response = call_payment_service(order, payment_url)
        return handle_response(response, payment_url)
    except Exception as error:
        logger.debug(f"Encountered error while calling payment service, error:{error}")
        log_and_raise_error(error)


def fetch_payment_url() -> str:
    logger.debug(f"Fetching SSM value for key: {PAYMENT_URL_SSM}")
    return aws_ssm_config.get_ssm_provider().get(PAYMENT_URL_SSM, max_age=900)


def call_payment_service(order: Order, payment_url: str) -> requests.Response:
    logger.debug(f"Calling payment service, orderId: {order.id}, url: {payment_url}")
    url = urlparse(payment_url)
    iam_auth = BotoAWSRequestsAuth(
        aws_host=url.netloc,
        aws_region=REGION,
        aws_service='execute-api'
    )

    response = requests.post(
        f"{payment_url}/ecommerce/payments/validate",
        json={
            "orderId": order.id,
            "userId": order.user_id,
            "total": order.get_total_amount()
        },
        auth=iam_auth
    )

    logger.debug(
        f"Get response from payment service, orderId:{order.id}, statusCode:{response.status_code}, res={response.json()}")

    if response.status_code in {429} or 500 <= response.status_code < 600:
        raise RetryableHTTPError(f"Retryable error: {response.status_code}")

    return response


def handle_response(response: requests.Response, payment_url: str) -> bool:
    if response.status_code != 200:
        raise DomainError(
            DomainCode.HTTP_ERROR,
            f"{payment_url}/ecommerce/payments/validate",
            response.status_code,
            response.json()
        )

    return True if response.status_code == 200 else False


def log_and_raise_error(error: Exception) -> None:
    logger.exception(error)
    logger.debug(f"Error encountered during product service validation: {error}")
    raise DomainError(DomainCode.UNKNOWN, str(error))