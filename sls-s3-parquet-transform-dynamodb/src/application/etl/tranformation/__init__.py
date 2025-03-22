"""
Transformation Module

This module contains transformation strategies for different data types,
following the Strategy Pattern to encapsulate different transformation algorithms.
"""

from application.etl.tranformation.base_transformer import DataTransformer, TransformationResult
from application.etl.tranformation.loan_application_transformer import LoanApplicationTransformer
from application.etl.tranformation.transformation_factory import DataTransformerFactory

__all__ = [
    'DataTransformer',
    'TransformationResult',
    'LoanApplicationTransformer',
    'DataTransformerFactory'
]