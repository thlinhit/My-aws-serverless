from functools import cache

from aws_lambda_powertools.utilities import parameters
from botocore.config import Config

from src.config.env import REGION
from src.log.logger import logger


@cache
def get_ssm_provider():
    config = Config(
        region_name=REGION,
        connect_timeout=1,
        retries={"total_max_attempts": 2, "max_attempts": 5}
    )
    return parameters.SSMProvider(config=config)

def get(ssm_key: str, max_age: int = 900) -> str:
    logger.debug(f"Fetching SSM value for key: {ssm_key}")
    return get_ssm_provider().get(ssm_key, max_age)