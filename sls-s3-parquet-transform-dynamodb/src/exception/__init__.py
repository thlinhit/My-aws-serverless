"""
Exception handling module for the application.

This module defines domain-specific exceptions and error codes,
providing a structured way to handle and report errors throughout the application.
"""

from exception.domain_code import DomainCode
from exception.domain_error import DomainError

__all__ = [
    'DomainCode',
    'DomainError'
]