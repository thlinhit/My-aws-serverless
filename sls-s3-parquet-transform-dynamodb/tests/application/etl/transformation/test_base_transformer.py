"""
Tests for the base transformer
"""
import pytest
from pyspark.sql.functions import lit, when, col

from application.etl.tranformation.base_transformer import DataTransformer, TransformationResult


class ConcreteTransformer(DataTransformer):
    """Concrete implementation of the abstract DataTransformer for testing"""
    
    def transform(self, df):
        """Implement the abstract method"""
        # Add an error_info column
        df_with_errors = df.withColumn(
            "error_info",
            lit(None).cast("string")  # All records are valid
        )
        
        # Partition the DataFrame
        valid_items, error_items = self._partition_dataframe(df_with_errors)
        
        # Return the result
        return TransformationResult(
            valid_items=valid_items,
            error_items=error_items,
            total_count=df.count(),
            valid_count=valid_items.count(),
            error_count=error_items.count()
        )


class TestBaseTransformer:
    """Test suite for the base transformer"""
    
    @pytest.fixture
    def transformer(self):
        """Create a concrete transformer for testing"""
        return ConcreteTransformer()
    
    def test_partition_dataframe_all_valid(self, transformer, loan_application_df):
        """Test partitioning a DataFrame with all valid records"""
        # Add an error_info column with all nulls (all valid)
        df_with_errors = loan_application_df.withColumn("error_info", lit(None))
        
        # Partition the DataFrame
        valid_items, error_items = transformer._partition_dataframe(df_with_errors)
        
        # Verify the results
        assert valid_items.count() == 2
        assert error_items.count() == 0
    
    def test_partition_dataframe_all_errors(self, transformer, loan_application_df):
        """Test partitioning a DataFrame with all error records"""
        # Add an error_info column with all non-nulls (all errors)
        df_with_errors = loan_application_df.withColumn("error_info", lit("Error"))
        
        # Partition the DataFrame
        valid_items, error_items = transformer._partition_dataframe(df_with_errors)
        
        # Verify the results
        assert valid_items.count() == 0
        assert error_items.count() == 2
    
    def test_partition_dataframe_mixed(self, transformer, loan_application_df):
        """Test partitioning a DataFrame with mixed valid and error records"""
        # Add an error_info column with some nulls and some non-nulls
        df_with_errors = loan_application_df.withColumn(
            "error_info",
            when(col("customer_id") == lit("12345"), lit(None)).otherwise("Error")
        )
        
        # Partition the DataFrame
        valid_items, error_items = transformer._partition_dataframe(df_with_errors)
        
        # Verify the results
        assert valid_items.count() == 1
        assert error_items.count() == 1
    
    def test_transformation_result(self, transformer, loan_application_df):
        """Test creating a transformation result"""
        # Transform the data
        result = transformer.transform(loan_application_df)
        
        # Verify the result
        assert isinstance(result, TransformationResult)
        assert result.total_count == 2
        assert result.valid_count == 2
        assert result.error_count == 0
        assert not result.valid_items.isEmpty()
        assert result.error_items.isEmpty()
