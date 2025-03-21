#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AWS Glue ETL job for processing Parquet files from S3 and loading them to DynamoDB.
This job follows Domain-Driven Design principles with clear separation of concerns.
"""

import sys
import time

# Import application components
from application.etl.transformation_strategies import TransformationStrategyFactory
# Import infrastructure components
from infrastructure.dynamodb_client import DynamoDBClient
from infrastructure.logger import logger


def main():
    # # Initialize logger with job context
    # logger = LogManager.setup_logger(
    #     log_level=args.get('log_level', 'INFO'),
    #     service="s3-to-dynamodb-etl"
    # )
    #
    # # Add job parameters to all logs
    # LogManager.append_keys(
    #     job_name=args['JOB_NAME'],
    #     source_bucket=args['source_bucket'],
    #     source_prefix=args['source_prefix'],
    #     target_table=args['target_dynamodb_table'],
    #     region=args['aws_region']
    # )

    # # Extract job parameters
    # source_bucket = args['source_bucket']
    # source_prefix = args['source_prefix']
    # target_dynamodb_table = args['target_dynamodb_table']
    # aws_region = args['aws_region']

    aws_region = 'eu-west-1'

    # Set up DynamoDB client
    dynamodb_client = DynamoDBClient(region=aws_region)

    # Log job start
    # LogManager.log_job_status(args['JOB_NAME'], "STARTING")

    # Record job start time
    job_start_time = time.time()

    try:
        logger.info(f"Start")
        # # Read data from S3 using Glue's built-in functionality
        # s3_path = f"s3://{source_bucket}/{source_prefix}"
        # logger.info("Reading data from S3", extra={"s3_path": s3_path})

        # Read Parquet files using Glue's DynamicFrame
        # dynamic_frame = glue_context.create_dynamic_frame.from_options(
        #     connection_type="s3",
        #     connection_options={
        #         "paths": [s3_path],
        #         "recurse": True
        #     },
        #     format="parquet"
        # )
        #
        # # Determine file type from the path
        # file_type = "LOAN_APPLICATION" if "loan-application" in source_prefix.lower() else "UNKNOWN"
        #
        # # Add file type to structured logs
        # LogManager.append_keys(file_type=file_type)
        #
        # # Skip processing if no data
        # if dynamic_frame.count() == 0:
        #     logger.warning("No data found to process. Exiting job.")
        #     LogManager.log_job_status(
        #         args['JOB_NAME'],
        #         "SUCCEEDED",
        #         input_count=0,
        #         output_count=0,
        #         start_time=job_start_time
        #     )
        #     job.commit()
        #     return
        #
        # # Convert to DataFrame for transformation
        # df = dynamic_frame.toDF()
        # record_count = df.count()
        # logger.info("Data loaded from S3", extra={"record_count": record_count})
        #
        # # Get appropriate transformation strategy
        # strategy = TransformationStrategyFactory.get_strategy(file_type)
        #
        # # Transform the data using the strategy
        # transformed_df = strategy.transform(
        #     df=df,
        #     target_table=target_dynamodb_table
        # )
        #
        # # Track start time for write operation
        # write_start_time = time.time()
        # logger.info("Starting distributed write to DynamoDB")
        #
        # # Use foreachPartition to write data in parallel
        # # We need to track success/error counts separately
        # success_count = sc.accumulator(0)
        # error_count = sc.accumulator(0)
        #
        # # Define a function to update accumulators
        # def process_and_update_metrics(partition):
        #     success, errors = dynamodb_client.process_partition_to_dynamodb(
        #         partition,
        #         table_name=target_dynamodb_table
        #     )
        #     success_count.add(success)
        #     error_count.add(errors)
        #
        # # Process all partitions
        # transformed_df.foreachPartition(process_and_update_metrics)
        #
        # # Get final counts from accumulators
        # total_success = success_count.value
        # total_errors = error_count.value
        #
        # # Record write duration
        # write_duration = time.time() - write_start_time

        # logger.info(
        #     "Completed distributed write to DynamoDB",
        #     extra={
        #         "records_written": total_success,
        #         "write_errors": total_errors,
        #         "write_duration_seconds": write_duration
        #     }
        # )

        # Log job success
        # LogManager.log_job_status(
        #     args['JOB_NAME'],
        #     "SUCCEEDED" if total_errors == 0 else "COMPLETED_WITH_ERRORS",
        #     input_count=record_count,
        #     output_count=total_success,
        #     start_time=job_start_time
        # )

    except Exception as e:
        # Log error and mark job as failed
        logger.exception(f"ETL job failed: {str(e)}")
        # LogManager.log_job_status(
        #     args['JOB_NAME'],
        #     "FAILED",
        #     start_time=job_start_time,
        #     error=str(e)
        # )
        raise


if __name__ == "__main__":
    main()