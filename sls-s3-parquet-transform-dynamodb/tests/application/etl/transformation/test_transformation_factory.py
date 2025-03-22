"""
Tests for the transformation factory
"""
import pytest

from application.etl.tranformation.base_transformer import DataTransformer
from application.etl.tranformation.loan_application_transformer import LoanApplicationTransformer
from application.etl.tranformation.transformation_factory import DataTransformerFactory
from exception.domain_code import DomainCode
from exception.domain_error import DomainError


class TestDataTransformerFactory:
    """Test suite for the data transformer factory"""

    def test_create_known_transformer(self):
        """Test creating a known transformer"""
        # Create a loan application transformer
        transformer = DataTransformerFactory.create("LOAN_APPLICATION")

        # Verify the transformer type
        assert isinstance(transformer, LoanApplicationTransformer)

    def test_create_unknown_transformer(self):
        """Test creating an unknown transformer"""
        # Try to create an unknown transformer
        with pytest.raises(DomainError) as excinfo:
            DataTransformerFactory.create("UNKNOWN_TYPE")

        # Verify the exception details
        assert excinfo.value.domain_code == DomainCode.NO_DATA_TRANSFORMER_FOUND
        assert excinfo.value.get_value("data_type") == "UNKNOWN_TYPE"

    def test_register_new_transformer(self):
        """Test registering a new transformer"""

        # Create a mock transformer class
        class MockTransformer(DataTransformer):
            def transform(self, df):
                pass

        # Register the new transformer
        DataTransformerFactory.register("MOCK_TYPE", MockTransformer)

        # Create the new transformer
        transformer = DataTransformerFactory.create("MOCK_TYPE")

        # Verify the transformer type
        assert isinstance(transformer, MockTransformer)

        # Clean up (remove the registered transformer)
        DataTransformerFactory._transformers.pop("MOCK_TYPE")