from abc import ABC, abstractmethod

import pandas as pd
from pyspark.sql import DataFrame
from pyspark.sql.functions import pandas_udf, struct, col
from pyspark.sql.types import MapType, StringType

from domain.models.loan_application import LoanApplication
from infrastructure.logger import logger


class TransformationStrategy(ABC):
    """Base class for transformation strategies"""
    
    @abstractmethod
    def transform(self, df: DataFrame, target_table: str) -> DataFrame:
        """Transform the DataFrame according to the strategy"""
        pass
    
    @abstractmethod
    def get_schema(self) -> MapType:
        """Get the output schema for the transformation"""
        pass


class LoanApplicationStrategy(TransformationStrategy):
    """Strategy for transforming loan application data"""
    
    def __init__(
        self,
        partition_key_pattern: str = "CUS#{customer_id}",
        sort_key_pattern: str = "LOAN_APP#{application_id}"
    ):
        self.partition_key_pattern = partition_key_pattern
        self.sort_key_pattern = sort_key_pattern
        self.error_count = 0

    def get_schema(self) -> MapType:
        return MapType(StringType(), StringType())
    
    def transform(self, df: DataFrame, target_table: str) -> DataFrame:
        logger.info(f"Transforming loan application data for DynamoDB table: {target_table}")
        
        # Define the pandas UDF for distributed transformation
        @pandas_udf(self.get_schema())
        def validate_and_transform_loan_app(batch_pd: pd.DataFrame) -> pd.Series:
            """
            Process a batch of records using pandas within a Spark executor.
            Each executor processes a partition of the data.
            """
            results = []
            batch_errors = 0
            
            for _, row in batch_pd.iterrows():
                try:
                    # Convert pandas row to dict
                    row_dict = row.to_dict()
                    
                    # Transform using Pydantic model
                    loan_app = LoanApplication(**row_dict)
                    dynamodb_item = loan_app.to_dynamodb_item(
                        partition_key_pattern=self.partition_key_pattern,
                        sort_key_pattern=self.sort_key_pattern
                    )
                    
                    # Convert all values to string for MapType compatibility
                    string_item = {k: str(v) if v is not None else None for k, v in dynamodb_item.items()}
                    results.append(string_item)
                    
                except Exception as e:
                    # Count errors and return None for invalid records
                    batch_errors += 1
                    results.append(None)
            
            # Add batch errors to the total (this is not thread-safe but gives an estimate)
            self.error_count += batch_errors
            
            return pd.Series(results)
        
        # Apply the UDF to create a new column with transformed data
        transformed_df = df.withColumn(
            "dynamodb_item", 
            validate_and_transform_loan_app(struct(*[col(c) for c in df.columns]))
        )
        
        # Filter out failed transformations
        valid_items_df = transformed_df.filter(transformed_df.dynamodb_item.isNotNull())
        
        valid_transformed_count = valid_items_df.count()
        self.logger.info(
            f"Transformed {valid_transformed_count} loan application records "
            f"(with ~{self.error_count} errors)"
        )
        
        return valid_items_df.select("dynamodb_item")


class TransformationStrategyFactory:
    """Factory for creating transformation strategies"""
    
    _strategies = {
        "LOAN_APPLICATION": LoanApplicationStrategy
    }
    
    @classmethod
    def get_strategy(cls, file_type: str) -> TransformationStrategy:
        """
        Get the appropriate transformation strategy for the given file type.
        
        Args:
            file_type: Type of file to transform (e.g., "LOAN_APPLICATION")
            
        Returns:
            Transformation strategy instance
            
        Raises:
            ValueError: If no transformation strategy is found for the given file type
        """
        if file_type not in cls._strategies:
            raise ValueError(
                f"No transformation strategy found for file type: {file_type}. "
                f"Supported file types are: {', '.join(cls._strategies.keys())}"
            )
        
        return cls._strategies[file_type]() 