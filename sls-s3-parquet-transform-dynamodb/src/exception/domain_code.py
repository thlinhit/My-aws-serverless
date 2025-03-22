"""
Domain error codes for the application.
Provides a standardized way to identify and describe errors.
"""
import re
from enum import Enum, unique


def convert_pattern(pattern: str) -> str:
    """
    Convert a pattern with {key} placeholders to key={key} format.

    Args:
        pattern: String pattern with {key} placeholders

    Returns:
        Converted pattern string with key={key} format
    """

    def replacer(match: re.Match) -> str:
        key = match.group(1)
        return f"{key}='{{{key}}}'"

    return re.sub(r'{(\w+)}', replacer, pattern)


@unique
class DomainCode(Enum):
    """
    Enumeration of domain error codes and their messages.
    Each code has a unique identifier and a message template.
    """
    UNKNOWN = (
        "000",
        "Generic Error. {error_message}",
    )
    NO_DATA_TRANSFORMER_FOUND = (
        "001",
        "No transformer found for data type. {data_type}",
    )
    DF_VALIDATION_ERROR = (
        "002",
        "Having error items, {data_type}, {total_count}, {error_count}",
    )
    DYNAMODB_ERROR = (
        "003",
        "Failed integrate with DynamoDB, {table_name}, {error_message}",
    )
    DYNAMODB_WRITE_FAILURE = (
        "004",
        "Failed to write items to DynamoDB table, {failed_count}, {total_count}, {table_name}, {data_type}",
    )
    PARQUET_READ_ERROR = (
        "005",
        "Failed to read Parquet file. {file_path}, {error_message}",
    )

    def __new__(cls, *values):
        """Create a new instance of the enum."""
        instance = object.__new__(cls)
        instance._value_ = values[0]
        return instance

    def __init__(self, _: str, internal_msg: str = None):
        """
        Initialize the enum value with a code and message.
        
        Args:
            _: The error code (already set in __new__)
            internal_msg: The error message template
        """
        self._internal_msg_ = convert_pattern(internal_msg)

    def __str__(self):
        """String representation of the error code."""
        return self.value

    @property
    def internal_msg(self):
        """Get the internal message template."""
        return self._internal_msg_

    @property
    def code(self):
        """Get the error code value."""
        return self._value_

    @property
    def external_code(self):
        """Get the external error code (same as value)."""
        return self.value