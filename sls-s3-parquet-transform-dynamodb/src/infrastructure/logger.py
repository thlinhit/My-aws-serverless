import os

from aws_lambda_powertools import Logger
from aws_lambda_powertools.logging.formatters.datadog import \
    DatadogLogFormatter

SERVICE_NAME = os.getenv("SERVICE_NAME", "unknown").upper()

logger = Logger(
    service=SERVICE_NAME,
    logger_formatter=DatadogLogFormatter(),
    log_uncaught_exceptions=True,
    log_record_order=["level", "message", "location", "function_request_id"],
)
