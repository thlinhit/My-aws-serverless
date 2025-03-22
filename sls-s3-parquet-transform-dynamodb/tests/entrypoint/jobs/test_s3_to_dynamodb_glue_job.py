"""
Tests for the S3 to DynamoDB Glue job
"""
import os
from unittest.mock import patch, MagicMock

import pytest

from entrypoint.jobs.s3_to_dynamodb_glue_job import process_parquet_file, main
from exception.domain_code import DomainCode
from exception.domain_error import DomainError


class TestS3ToDynamoDBGlueJob:
    """Test suite for the S3 to DynamoDB Glue job"""
    
    @pytest.fixture
    def mock_etl_service(self):
        """Mock ETL service"""
        mock_service = MagicMock()
        mock_service.process_data.return_value = {
            "processed": 2,
            "errors": 0,
            "total": 2,
            "message": ""
        }
        return mock_service
    
    @pytest.fixture
    def mock_parquet_reader(self, loan_application_df):
        """Mock Parquet reader"""
        mock_reader = MagicMock()
        mock_reader.read_parquet.return_value = loan_application_df
        mock_reader.get_data_info.return_value = {
            "row_count": 2,
            "column_count": 12,
            "columns": ["customer_id", "application_id", "status"]
        }
        return mock_reader
    
    def test_process_parquet_file_success(self, mock_etl_service, mock_parquet_reader):
        """Test processing a Parquet file successfully"""
        # Mock the dependencies
        with patch('entrypoint.jobs.s3_to_dynamodb_glue_job.LocalParquetReader', return_value=mock_parquet_reader), \
             patch('entrypoint.jobs.s3_to_dynamodb_glue_job.ETLService', return_value=mock_etl_service):
            
            # Process the file
            result = process_parquet_file(
                file_path="test.parquet",
                file_type="LOAN_APPLICATION",
                table_name="test_table"
            )
        
        # Verify the result
        assert result["processed_count"] == 2
        assert result["error_count"] == 0
        assert result["total_count"] == 2
        
        # Verify the dependencies were called correctly
        mock_parquet_reader.read_parquet.assert_called_once_with("test.parquet")
        mock_parquet_reader.get_data_info.assert_called_once()
        mock_etl_service.process_data.assert_called_once()
    
    def test_process_parquet_file_empty_data(self, mock_parquet_reader):
        """Test processing a Parquet file with no data"""
        # Configure the mock to return an empty DataFrame
        empty_df = MagicMock()
        empty_df.count.return_value = 0
        mock_parquet_reader.read_parquet.return_value = empty_df
        
        # Mock the dependencies
        with patch('entrypoint.jobs.s3_to_dynamodb_glue_job.LocalParquetReader', return_value=mock_parquet_reader):
            
            # Process the file
            result = process_parquet_file(
                file_path="empty.parquet",
                file_type="LOAN_APPLICATION",
                table_name="test_table"
            )
        
        # Verify the result
        assert result["status"] == "completed"
        assert "No data to process" in result["message"]
    
    def test_process_parquet_file_error(self, mock_parquet_reader):
        """Test processing a Parquet file with an error"""
        # Configure the mock to raise an exception
        mock_etl_service = MagicMock()
        mock_etl_service.process_data.side_effect = DomainError(
            DomainCode.DYNAMODB_WRITE_FAILURE,
            failed_count=1,
            total_count=2,
            table_name="test_table",
            data_type="LOAN_APPLICATION"
        )
        
        # Mock the dependencies
        with patch('entrypoint.jobs.s3_to_dynamodb_glue_job.LocalParquetReader', return_value=mock_parquet_reader), \
             patch('entrypoint.jobs.s3_to_dynamodb_glue_job.ETLService', return_value=mock_etl_service), \
             pytest.raises(DomainError) as excinfo:
            
            # Process the file
            process_parquet_file(
                file_path="test.parquet",
                file_type="LOAN_APPLICATION",
                table_name="test_table"
            )
        
        # Verify the exception
        assert excinfo.value.domain_code == DomainCode.DYNAMODB_WRITE_FAILURE
        assert excinfo.value.get_value("failed_count") == 1
        assert excinfo.value.get_value("total_count") == 2
    
    def test_main_success(self):
        """Test the main function with successful processing"""
        # Mock the process_parquet_file function
        mock_result = {
            "processed_count": 2,
            "error_count": 0,
            "total_count": 2
        }
        
        # Mock the dependencies
        with patch('entrypoint.jobs.s3_to_dynamodb_glue_job.process_parquet_file', return_value=mock_result):
            
            # Run the main function
            exit_code = main()
        
        # Verify the exit code
        assert exit_code == 0
    
    def test_main_domain_error(self):
        """Test the main function with a domain error"""
        # Mock the process_parquet_file function to raise a domain error
        domain_error = DomainError(
            DomainCode.DYNAMODB_WRITE_FAILURE,
            failed_count=1,
            total_count=2,
            table_name="test_table",
            data_type="LOAN_APPLICATION"
        )
        
        # Mock the dependencies
        with patch('entrypoint.jobs.s3_to_dynamodb_glue_job.process_parquet_file', side_effect=domain_error):
            
            # Run the main function
            exit_code = main()
        
        # Verify the exit code
        assert exit_code == 1
    
    def test_main_unexpected_error(self):
        """Test the main function with an unexpected error"""
        # Mock the process_parquet_file function to raise an unexpected error
        unexpected_error = Exception("Unexpected error")
        
        # Mock the dependencies
        with patch('entrypoint.jobs.s3_to_dynamodb_glue_job.process_parquet_file', side_effect=unexpected_error), \
             pytest.raises(DomainError) as excinfo:
            
            # Run the main function
            main()
        
        # Verify the exception
        assert excinfo.value.domain_code == DomainCode.UNKNOWN
        assert "Unexpected error" in excinfo.value.get_value("error_message")
