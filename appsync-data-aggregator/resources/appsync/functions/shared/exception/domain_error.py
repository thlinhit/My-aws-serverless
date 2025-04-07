"""
Domain error exception for the application.
Provides a standardized way to raise and handle domain-specific errors.
"""
from typing import Any, Dict, Optional

from exception.domain_code import DomainCode


class DomainError(Exception):
    """
    Domain-specific exception that includes an error code and values.
    This provides rich error information and consistent error handling.
    """
    
    def __init__(self, domain_code: DomainCode, **values):
        """
        Initialize a domain error.
        
        Args:
            domain_code: The error code enum value
            **values: The values to substitute in the error message template
        """
        self.domain_code = domain_code
        self.values = values
        self.message = "[{}] - {}".format(
            domain_code.external_code, domain_code.internal_msg.format(**values)
        )
        super().__init__(self.message)

    def get_value(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Get a value from the error values dictionary.
        
        Args:
            key: The key to look up
            default: The default value to return if the key is not found
            
        Returns:
            The value for the key, or the default if not found
        """
        return self.values.get(key, default)
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the error to a dictionary representation.
        
        Returns:
            Dictionary representation of the error
        """
        return {
            "code": self.domain_code.code,
            "message": self.message,
            "values": self.values
        }