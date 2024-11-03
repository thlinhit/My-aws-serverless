import os
from urllib.parse import urlparse

import requests
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth
from tenacity import retry, retry_if_exception_type, wait_exponential_jitter, stop_after_attempt

from src.config import aws_ssm_config
from src.config.env import REGION
from src.connector.retryable_http_error import RetryableHTTPError
from src.domain.order import Order
from src.log.logger import logger

# The payment URL should be set as a parameter. I added it to SSM for demonstration convenience.
PRODUCT_URL_SSM = os.getenv("PRODUCT_URL_SSM")


@retry(
    retry=retry_if_exception_type(RetryableHTTPError),
    wait=wait_exponential_jitter(max=10),
    stop=stop_after_attempt(3)
)
def validate(order: Order) -> bool:
    logger.info(f"Validating payment, orderId:{order.id}")
    payment_url: str = aws_ssm_config.get_ssm_provider().get_parameters_by_name(PRODUCT_URL_SSM, max_age=900)
    url = urlparse(payment_url)
    iam_auth = BotoAWSRequestsAuth(aws_host=url.netloc,
                                   aws_region=REGION,
                                   aws_service='execute-api')
    response = requests.post(
        payment_url + "/ecommerce/products/validate",
        json={
            "products": order.products
        },
        auth=iam_auth
    )

    if response.status_code in {429} or 500 <= response.status_code < 600:
        raise RetryableHTTPError(f"Retryable error: {response.status_code}")

    body = response.json()
    logger.info(f"Payment validated, orderId:{order.id}, invalidProducts:{body.get("products", [])}")
    return len(body.get("products", [])) == 0
