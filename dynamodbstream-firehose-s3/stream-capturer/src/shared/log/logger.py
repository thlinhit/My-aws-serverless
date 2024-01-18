from aws_lambda_powertools import Logger
from aws_lambda_powertools.logging.formatters.datadog import (
    DatadogLogFormatter,
)

logger = Logger(logger_formatter=DatadogLogFormatter(), log_record_order=["level", "message", "location", "function_request_id"])
