"""
Tests for the ETL service
"""
from unittest.mock import MagicMock, patch

import pytest
from pyspark.sql import DataFrame

from application.etl.etl_service import ETLService
from pyspark.sql.types import StructType

from application.etl.tranformation.base_transformer import TransformationResult
from exception.domain_code import DomainCode
from exception.domain_error import DomainError


class TestETLService:
    """Test suite for the ETL service"""

    @pytest.fixture
    def mock_transformer_factory(self):
        """Mock transformer factory"""
        mock_factory = MagicMock()
        mock_transformer = MagicMock()
        mock_factory.create.return_value = mock_transformer
        return mock_factory, mock_transformer

    @pytest.fixture
    def mock_dynamodb_client(self):
        """Mock DynamoDB client"""
        return MagicMock()

    def test_process_data_success(self, loan_application_df, mock_transformer_factory, mock_dynamodb_client):
        """Test successful data processing"""
        mock_factory, mock_transformer = mock_transformer_factory

        # Configure mock transformer
        mock_transformer.transform.return_value = TransformationResult(
            valid_items=loan_application_df,
            error_items=loan_application_df.limit(0),  # Empty DataFrame
            total_count=2,
            valid_count=2,
            error_count=0
        )

        # Configure mock DynamoDB client
        mock_dynamodb_client.write_partition_to_dynamodb = MagicMock()
        mock_dynamodb_client.write_partition_to_dynamodb.return_value.failed_items = []

        # Create service with mocks
        service = ETLService(
            transformer_factory=mock_factory,
            dynamodb_client=mock_dynamodb_client
        )

        # Mock the _persist_to_dynamodb method to return empty list (no failures)
        with patch.object(service, '_persist_to_dynamodb', return_value=[]):
            result = service.process_data(
                df=loan_application_df,
                data_type="LOAN_APPLICATION",
                table_name="test_table"
            )

        # Verify the result
        assert result["processed"] == 2
        assert result["errors"] == 0
        assert result["total"] == 2
        assert "completed successfully" in result["message"]

        # Verify the transformer was called correctly
        mock_factory.create.assert_called_once_with("LOAN_APPLICATION")
        mock_transformer.transform.assert_called_once()

    def test_process_data_with_validation_errors(self, loan_application_df, mock_transformer_factory,
                                                 mock_dynamodb_client):
        """Test data processing with validation errors"""
        mock_factory, mock_transformer = mock_transformer_factory

        # Configure mock transformer to return errors
        mock_transformer.transform.return_value = TransformationResult(
            valid_items=loan_application_df.limit(1),  # One valid item
            error_items=loan_application_df.limit(1),  # One error item
            total_count=2,
            valid_count=1,
            error_count=1
        )

        # Create service with mocks
        service = ETLService(
            transformer_factory=mock_factory,
            dynamodb_client=mock_dynamodb_client
        )

        # Test that it raises the expected exception
        with pytest.raises(DomainError) as excinfo:
            service.process_data(
                df=loan_application_df,
                data_type="LOAN_APPLICATION",
                table_name="test_table"
            )

        # Verify the exception details
        assert excinfo.value.domain_code == DomainCode.DF_VALIDATION_ERROR
        assert excinfo.value.get_value("data_type") == "LOAN_APPLICATION"
        assert excinfo.value.get_value("total_count") == 2
        assert excinfo.value.get_value("error_count") == 1

    def test_process_data_with_dynamodb_failures(self, loan_application_df, mock_transformer_factory,
                                                 mock_dynamodb_client):
        """Test data processing with DynamoDB write failures"""
        mock_factory, mock_transformer = mock_transformer_factory

        # Configure mock transformer
        mock_transformer.transform.return_value = TransformationResult(
            valid_items=loan_application_df,
            error_items=loan_application_df.limit(0),  # Empty DataFrame
            total_count=2,
            valid_count=2,
            error_count=0
        )

        # Create service with mocks
        service = ETLService(
            transformer_factory=mock_factory,
            dynamodb_client=mock_dynamodb_client
        )

        # Mock the _persist_to_dynamodb method to return failures
        failed_items = [{"pk": "CUS#12345", "sk": "LOAN_APP#APP001"}]
        with patch.object(service, '_persist_to_dynamodb', return_value=failed_items):
            with pytest.raises(DomainError) as excinfo:
                service.process_data(
                    df=loan_application_df,
                    data_type="LOAN_APPLICATION",
                    table_name="test_table"
                )

        # Verify the exception details
        assert excinfo.value.domain_code == DomainCode.DYNAMODB_WRITE_FAILURE
        assert excinfo.value.get_value("failed_count") == 1
        assert excinfo.value.get_value("total_count") == 2
        assert excinfo.value.get_value("table_name") == "test_table"

    def test_process_empty_dataframe(self, spark, mock_transformer_factory, mock_dynamodb_client):
        """Test processing an empty DataFrame"""
        # Create an empty DataFrame
        empty_df = spark.createDataFrame([], schema=StructType([]))

        # Create service with mocks
        service = ETLService(
            transformer_factory=mock_transformer_factory[0],
            dynamodb_client=mock_dynamodb_client
        )

        # Process the empty DataFrame
        result = service.process_data(
            df=empty_df,
            data_type="LOAN_APPLICATION",
            table_name="test_table"
        )

        # Verify the result
        assert result["processed"] == 0
        assert result["errors"] == 0
        assert "No data to process" in result["message"]

        # Verify the transformer was not called
        mock_transformer_factory[0].create.assert_not_called()