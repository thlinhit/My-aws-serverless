from enum import Enum, unique

import re

def convert_pattern(pattern: str) -> str:
    def replacer(match: re.Match) -> str:
        key = match.group(1)
        return f"{key}='{{{key}}}'"

    return re.sub(r'{(\w+)}', replacer, pattern)

@unique
class DomainCode(Enum):
    UNKNOWN = (
        "1340000",
        "Generic Error. {error_message}",
    )
    NO_DATA_TRANSFORMER_FOUND = (
        "1340001",
        "No transformer found for data type. {data_type}",
    )
    VALIDATION_ERROR = (
        "1340002",
        "Validation Error. {error_message}",
    )
    DYNAMODB_ERROR = (
        "1340003",
        "Failed integrate with DynamoDB, {table_name}, {error_message}",
    )

    def __new__(cls, *values):
        instance = object.__new__(cls)
        instance._value_ = values[0]
        return instance

    def __init__(self, _: str, internal_msg: str = None):
        self._internal_msg_ = convert_pattern(internal_msg)

    def __str__(self):
        return self.value

    @property
    def internal_msg(self):
        return self._internal_msg_

    @property
    def code(self):
        return self._value_

    @property
    def external_code(self):
        return self.value
