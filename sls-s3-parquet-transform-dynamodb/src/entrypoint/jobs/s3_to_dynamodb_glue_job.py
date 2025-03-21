#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AWS Glue ETL job for processing Parquet files from S3 and loading them to DynamoDB.
This job follows Domain-Driven Design principles with clear separation of concerns.
"""
import os
import time

from application.etl.tranformation.transformation_factory import DataTransformerFactory
from exception.domain_code import DomainCode
from exception.domain_error import DomainError
from infrastructure.dynamodb_client import DynamoDBClient
from infrastructure.local_parquet_reader import LocalParquetReader
from infrastructure.logger import logger

TABLE = os.getenv("TABLE", "dummy")


def main():
    # Set up clients
    parquet_reader = LocalParquetReader()

    # Record job start time
    job_start_time = time.time()

    try:
        file_type = "LOAN_APPLICATION"
        logger.info(f"Starting Parquet file processing, fileType={file_type}")

        # Read and analyze the Parquet file
        df = parquet_reader.read_parquet("input.parquet")
        data_info = parquet_reader.get_data_info(df)

        # Skip processing if no data
        if df.count() == 0:
            logger.warning("No data found to process. Exiting job.")
            return

        logger.info("Data loaded", extra={"record_count": data_info['row_count']})

        # Get appropriate transformation strategy
        transformer = DataTransformerFactory.create(file_type)

        # Transform the data using the strategy
        transformation_result = transformer.transform(
            df=df
        )

        logger.info("Valid items:")
        logger.info(transformation_result.valid_items.show(truncate=False))

        logger.info("Invalid items:")
        logger.info(transformation_result.error_items.show(truncate=False))

        def write_to_dynamodb(partition):
            dynamodb_update_result = DynamoDBClient.write_partition_to_dynamodb(
                partition,
                table_name=TABLE
            )
            return dynamodb_update_result.failed_items


        failed_items = transformation_result.valid_items.rdd.mapPartitions(lambda x: write_to_dynamodb(x)).collect()

        for item in failed_items:
            logger.error(item)

        # Log final statistics
        logger.info(
            f"Job completed successfully. "
            f"Total records: {transformation_result.total_count}, "
            f"Valid records: {transformation_result.valid_count}, "
            f"Error records: {transformation_result.error_count}"
        )
    except DomainError as domain_error:
        logger.exception(f"test: {str(domain_error)}")
        raise domain_error
    except Exception as e:
        logger.exception(f"ETL job failed: {str(e)}")
        raise DomainError(DomainCode.UNKNOWN, error_message=str(e))


if __name__ == "__main__":
    main()
