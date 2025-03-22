"""
Factory for creating data transformers
"""
from typing import Dict, Type

from application.etl.tranformation.base_transformer import DataTransformer
from application.etl.tranformation.loan_application_transformer import LoanApplicationTransformer
from exception.domain_code import DomainCode
from exception.domain_error import DomainError


class DataTransformerFactory:
    """
    Factory class for creating data transformers according to the factory pattern.
    Supports extensibility by allowing new transformers to be registered.
    """

    # Registry of available transformers
    _transformers: Dict[str, Type[DataTransformer]] = {
        "LOAN_APPLICATION": LoanApplicationTransformer
    }

    @classmethod
    def create(cls, data_type: str) -> DataTransformer:
        """
        Create a transformer instance based on data type.

        Args:
            data_type: The type of data to transform

        Returns:
            DataTransformer: An instance of the appropriate transformer

        Raises:
            DomainError: If no transformer is found for the given data type
        """
        if data_type not in cls._transformers:
            raise DomainError(DomainCode.NO_DATA_TRANSFORMER_FOUND, data_type=data_type)
        return cls._transformers[data_type]()

    @classmethod
    def register(cls, data_type: str, transformer_class: Type[DataTransformer]) -> None:
        """
        Register a new transformer class for a data type.

        Args:
            data_type: The data type identifier
            transformer_class: The transformer class to register
        """
        cls._transformers[data_type] = transformer_class