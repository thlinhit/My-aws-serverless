from functools import cache

from aws_lambda_powertools.utilities import parameters
from botocore.config import Config

from src.config.env import REGION


@cache
def get_ssm_provider():
    config = Config(
        region_name=REGION,
        connect_timeout=1,
        retries={"total_max_attempts": 2, "max_attempts": 5}
    )
    return parameters.SSMProvider(config=config)
