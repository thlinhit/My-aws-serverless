"""
Tests for the loan application transformer
"""
import pytest
from pyspark.sql.functions import lit

from application.etl.tranformation.loan_application_transformer import LoanApplicationTransformer
from infrastructure import logger


class TestLoanApplicationTransformer:
    """Test suite for the loan application transformer"""

    @pytest.fixture
    def transformer(self):
        """Create a loan application transformer"""
        return LoanApplicationTransformer()

    def test_transform_valid_data(self, transformer, loan_application_df):
        """Test transforming valid loan application data"""
        # Transform the data
        result = transformer.transform(loan_application_df)

        # Verify the result
        assert result.total_count == 2
        assert result.valid_count == 2
        assert result.error_count == 0
        assert not result.valid_items.isEmpty()
        assert result.error_items.isEmpty()

        # Check that the dynamodb_item column was created
        assert "dynamodb_item" in result.valid_items.columns

    def test_transform_with_validation_errors(self, transformer, loan_application_df, spark):
        """Test transforming data with validation errors"""
        # Create a DataFrame with invalid data (missing required fields)
        invalid_df = loan_application_df.withColumn("customer_id", lit(None))

        # Transform the data
        result = transformer.transform(invalid_df)

        # Verify the result
        assert result.total_count == 2
        assert result.valid_count < 2  # Some records should be invalid
        assert result.error_count > 0  # Should have error records
        assert not result.error_items.isEmpty()

    def test_process_decline_reasons(self, transformer, loan_application_df):
        """Test processing decline reasons"""
        # Get the declined application
        declined_df = loan_application_df.filter(f"status = 'DECLINED'")

        logger.info(declined_df.show())
        # Process decline reasons
        result_df = transformer._process_decline_reasons(declined_df)

        # Collect the result for inspection
        result = result_df.collect()[0]

        # Verify decline reasons were processed correctly
        decline_reasons = result["decline_reasons"]
        assert len(decline_reasons) > 0
        assert "Insufficient income" in decline_reasons
        assert "High debt ratio" in decline_reasons

    def test_create_dynamodb_structure(self, transformer, loan_application_df):
        """Test creating DynamoDB structure"""
        # Add error_info column (required by the method)
        df_with_error_info = loan_application_df.withColumn("error_info", lit(None)).withColumn("decline_reasons", lit(None))

        # Create DynamoDB structure
        result_df = transformer._create_dynamodb_structure(df_with_error_info)

        # Verify the result
        assert "dynamodb_item" in result_df.columns

        # Check the structure of dynamodb_item for a valid record
        valid_item = result_df.filter("error_info IS NULL").select("dynamodb_item").collect()[0][0]
        assert "pk" in valid_item
        assert "sk" in valid_item
        assert valid_item["pk"].startswith("CUS#")
        assert valid_item["sk"].startswith("LOAN_APP#")