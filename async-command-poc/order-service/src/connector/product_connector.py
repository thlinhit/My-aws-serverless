# src/connector/product_validator.py

import os
from urllib.parse import urlparse

import requests
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth
from tenacity import retry, retry_if_exception_type, wait_exponential_jitter, stop_after_attempt

from src.config import aws_ssm_config
from src.config.env import REGION
from src.connector.retryable_http_error import RetryableHTTPError
from src.domain.order import Order
from src.exception.domain_code import DomainCode
from src.exception.domain_error import DomainError
from src.log.logger import logger

# The product URL should be set as a parameter. I added it to SSM for demonstration convenience.
PRODUCT_URL_SSM = os.getenv("PRODUCT_URL_SSM")


@retry(
    retry=retry_if_exception_type(RetryableHTTPError),
    wait=wait_exponential_jitter(max=10),
    stop=stop_after_attempt(3)
)
def validate(order: Order) -> bool:
    try:
        product_url = aws_ssm_config.get(PRODUCT_URL_SSM, max_age=900)
        response = call_product_service(order, product_url)
        return handle_response(response, order.id, product_url)
    except Exception as error:
        log_and_raise_error(error)


def call_product_service(order: Order, product_url: str) -> requests.Response:
    logger.debug(f"Calling product service, orderId: {order.id}, url: {product_url}")
    url = urlparse(product_url)
    iam_auth = BotoAWSRequestsAuth(
        aws_host=url.netloc,
        aws_region=REGION,
        aws_service='execute-api'
    )

    response = requests.post(
        f"{product_url}/ecommerce/products/validate",
        json={"products": [product.model_dump(by_alias=True) for product in order.products]},
        auth=iam_auth
    )

    logger.debug(
        f"Received response from product service, orderId: {order.id}, "
        f"statusCode: {response.status_code}, response: {response.json()}"
    )

    if response.status_code in {429} or 500 <= response.status_code < 600:
        raise RetryableHTTPError(f"Retryable error: {response.status_code}")

    return response


def handle_response(response: requests.Response, order_id: str, product_url: str) -> bool:
    if response.status_code != 200:
        raise DomainError(
            DomainCode.HTTP_ERROR,
            f"{product_url}/ecommerce/products/validate",
            response.status_code,
            response.json()
        )

    body = response.json()
    logger.info(f"Order validation result, orderId: {order_id}, invalidProducts: {body.get('products', [])}")
    return len(body.get("products", [])) == 0


def log_and_raise_error(error: Exception) -> None:
    logger.exception(error)
    logger.debug(f"Error encountered during product service validation: {error}")
    raise DomainError(DomainCode.UNKNOWN, str(error))
