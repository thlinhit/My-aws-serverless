from src.shared.exception.domain_code import DomainCode
from src.shared.exception.domain_error import DomainError
from src.shared.utils import json_util


def build_dlq_message(function_name: str, exception: Exception, transaction_key=None, **kwargs) -> str:
    result = {
        "function": function_name,
        "errorCode": exception.domain_code.external_code if isinstance(exception, DomainError) else DomainCode.UNKNOWN.external_code,
        "transactionKey": transaction_key,
        "errorMessage": str(exception),
    }

    for kwarg in kwargs.items():
        result[kwarg[0]] = kwarg[1]
    return json_util.dumps(result)
