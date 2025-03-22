#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AWS Glue ETL job for processing Parquet files from S3 and loading them to DynamoDB.
This job follows Domain-Driven Design principles with clear separation of concerns.
"""
import os
os.environ["SERVICE_NAME"] = "SPL_ETL_JOB" # dirty code which is just used for demonstrating
import sys
import time
from typing import Dict, Any

from application.etl.etl_service import ETLService
from exception.domain_code import DomainCode
from exception.domain_error import DomainError
from infrastructure.local_parquet_reader import LocalParquetReader
from infrastructure.logger import logger

# Environment configuration with sensible defaults
TABLE = os.getenv("TABLE", "dummy_table")
# Set default file type - in a real-world scenario, this could come from Glue job parameters
DEFAULT_FILE_TYPE = "LOAN_APPLICATION"
PARQUET_FILE_PATH = os.getenv("PARQUET_FILE_PATH", "input.parquet")


def process_parquet_file(file_path: str, file_type: str, table_name: str) -> Dict[str, Any]:
    """
    Process a Parquet file and load the transformed data to DynamoDB.
    
    Args:
        file_path: Path to the Parquet file
        file_type: Type of data in the file
        table_name: DynamoDB table name
        
    Returns:
        Dictionary containing job results
        
    Raises:
        DomainError: If an error occurs during processing
    """
    # Initialize infrastructure components
    parquet_reader = LocalParquetReader()
    etl_service = ETLService()
    
    logger.info(
        f"Starting Parquet file processing",
        extra={
            "file_path": file_path,
            "file_type": file_type,
            "table_name": table_name
        }
    )
    
    # Read and analyze the Parquet file
    df = parquet_reader.read_parquet(file_path)
    data_info = parquet_reader.get_data_info(df)
    
    # Skip processing if no data
    if df.count() == 0:
        logger.warning("No data found to process. Exiting job.")
        return {
            "status": "completed",
            "message": "No data to process",
            "record_count": 0
        }
    
    logger.info(
        "Data loaded successfully",
        extra={"record_count": data_info['row_count']}
    )
    
    # Process data through ETL service
    result = etl_service.process_data(
        df=df,
        data_type=file_type,
        table_name=table_name
    )
    
    # Return job results
    return {
        "status": "completed",
        "processed_count": result["processed"],
        "error_count": result["errors"],
        "total_count": result["total"],
        "message": result["message"]
    }


def main() -> int:
    """
    Main entry point for the Glue job.
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    start_time = time.time()
    
    try:
        # Get file type from parameters or use default
        file_type = DEFAULT_FILE_TYPE
        
        # Process the file
        result = process_parquet_file(
            file_path=PARQUET_FILE_PATH,
            file_type=file_type,
            table_name=TABLE
        )
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Log job completion
        logger.info(
            "Job completed successfully",
            extra={
                "execution_time_seconds": execution_time,
                "processed_count": result.get("processed_count", 0),
                "error_count": result.get("error_count", 0),
                "total_count": result.get("total_count", 0)
            }
        )
        
        return 0  # Success exit code
        
    except DomainError as domain_error:
        logger.error(
            "Domain error occurred",
            extra={
                "error_code": domain_error.domain_code.code,
                "error_message": str(domain_error),
                "execution_time_seconds": time.time() - start_time
            }
        )
        return 1  # Error exit code
        
    except Exception as e:
        logger.exception(
            "Unexpected error occurred",
            extra={
                "error_message": str(e),
                "execution_time_seconds": time.time() - start_time
            }
        )
        # Wrap generic exceptions in domain error for consistent handling
        raise DomainError(DomainCode.UNKNOWN, error_message=str(e))


if __name__ == "__main__":
    sys.exit(main())
