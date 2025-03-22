"""
ETL Service module for orchestrating ETL operations
"""
from typing import Dict, Any, Optional, List

from pyspark.sql import DataFrame

from application.etl.tranformation.transformation_factory import DataTransformerFactory
from exception.domain_code import DomainCode
from exception.domain_error import DomainError
from infrastructure.dynamodb_client import DynamoDBClient
from infrastructure.logger import logger


class ETLService:
    """
    Service for orchestrating ETL processes, following the application layer pattern.
    Coordinates various infrastructure components and domain services to process data.
    """

    def __init__(self, transformer_factory=None, dynamodb_client=None):
        """
        Initialize the ETL service with required dependencies.

        Args:
            transformer_factory: Factory for creating data transformers
            dynamodb_client: Client for interacting with DynamoDB
        """
        self.transformer_factory = transformer_factory or DataTransformerFactory
        self.dynamodb_client = dynamodb_client or DynamoDBClient

    def process_data(self, df: DataFrame, data_type: str, table_name: str) -> Dict[str, Any]:
        """
        Process data through transformation and persistence.

        Args:
            df: DataFrame containing data to process
            data_type: Type of data to determine appropriate transformer
            table_name: Target DynamoDB table name

        Returns:
            Dictionary containing processing statistics
        """
        logger.info(f"Processing {data_type} data", extra={"record_count": df.count()})

        # Skip processing if no data
        if df.count() == 0:
            logger.warning("No data found to process")
            return {"processed": 0, "errors": 0, "message": "No data to process"}

        try:
            # Get appropriate transformation strategy
            transformer = self.transformer_factory.create(data_type)

            # Transform the data using the strategy
            transformation_result = transformer.transform(df=df)

            if transformation_result.error_count > 0:
                # TODO: discuss: should write failed items into S3 ??
                raise DomainError(DomainCode.DF_VALIDATION_ERROR,
                                  data_type=data_type,
                                  total_count=transformation_result.total_count,
                                  error_count=transformation_result.error_count)

            # Process valid items
            failed_items = self._persist_to_dynamodb(
                transformation_result.valid_items,
                table_name
            )

            if len(failed_items) > 0:
                # TODO: discuss: should write failed items into S3 ??
                raise DomainError(DomainCode.DYNAMODB_WRITE_FAILURE,
                                  failed_count=len(failed_items),
                                  total_count=transformation_result.valid_count,
                                  table_name=table_name,
                                  data_type=data_type)


            logger.info(
                f"{data_type} processing completed, total_records={transformation_result.total_count}"
            )

            return {
                "processed": transformation_result.valid_count,
                "errors": transformation_result.error_count + len(failed_items),
                "total": transformation_result.total_count,
                "message": "Processing completed successfully"
            }

        except DomainError as e:
            logger.error(f"Domain error during processing: {str(e)}")
            raise
        except Exception as e:
            logger.exception(f"Error during data processing: {str(e)}")
            raise DomainError(DomainCode.UNKNOWN, error_message=str(e))

    def _persist_to_dynamodb(self, items_df: DataFrame, table_name: str) -> List[Dict[str, Any]]:
        """
        Persist transformed items to DynamoDB.

        Args:
            items_df: DataFrame containing items to persist
            table_name: Target DynamoDB table name

        Returns:
            List of failed items
        """
        logger.info(f"Persisting {items_df.count()} items to DynamoDB table '{table_name}'")

        def write_to_dynamodb(partition):
            dynamodb_update_result = self.dynamodb_client.write_partition_to_dynamodb(
                partition,
                table_name=table_name
            )
            return dynamodb_update_result.failed_items

        # Use mapPartitions for better performance with Spark RDDs
        return items_df.rdd.mapPartitions(write_to_dynamodb).collect()
