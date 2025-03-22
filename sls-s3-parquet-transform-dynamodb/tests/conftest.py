"""
Shared test fixtures for the entire test suite
"""
import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict, Any, List

import boto3
import pytest
from moto import mock_dynamodb
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType, DecimalType

from exception.domain_code import DomainCode
from exception.domain_error import DomainError


@pytest.fixture(scope="session")
def spark():
    """Create a Spark session for testing"""
    spark = (SparkSession.builder
             .appName("TestSession")
             .master("local[2]")
             .config("spark.driver.host", "localhost")
             .config("spark.driver.bindAddress", "localhost")
             .config("spark.sql.shuffle.partitions", "2")
             .config("spark.default.parallelism", "2")
             .getOrCreate())

    yield spark

    # Clean up
    spark.stop()


@pytest.fixture
def sample_loan_application_data() -> List[Dict[str, Any]]:
    """Sample loan application data for testing"""
    return [
        {
            "customer_id": "12345",
            "application_id": "APP001",
            "date_application_created": "15-03-2025 14:30:00",
            "status": "Approved",
            "requested_amount": Decimal("5000.00"),
            "accepted_amount": Decimal("4500.00"),
            "debtor_account_number": "ACC123456",
            "contract_date": "20/03/2025",
            "gross_income": Decimal("60000.00"),
            "decline_reason_1": None,
            "decline_reason_2": None,
            "decline_reason_3": None
        },
        {
            "customer_id": "67890",
            "application_id": "APP002",
            "date_application_created": "16-03-2025 14:30:00",
            "status": "DECLINED",
            "requested_amount": Decimal("10000.00"),
            "accepted_amount": None,
            "debtor_account_number": "ACC789012",
            "contract_date": None,
            "gross_income": Decimal("45000.00"),
            "decline_reason_1": "Insufficient income",
            "decline_reason_2": "High debt ratio",
            "decline_reason_3": None
        }
    ]


@pytest.fixture
def loan_application_df(spark, sample_loan_application_data) -> DataFrame:
    """Create a DataFrame with sample loan application data"""
    schema = StructType([
        StructField("customer_id", StringType(), True),
        StructField("application_id", StringType(), True),
        StructField("date_application_created", StringType(), True),
        StructField("status", StringType(), True),
        StructField("requested_amount", DecimalType(10, 2), True),
        StructField("accepted_amount", DecimalType(10, 2), True),
        StructField("debtor_account_number", StringType(), True),
        StructField("contract_date", StringType(), True),
        StructField("gross_income", DecimalType(10, 2), True),
        StructField("decline_reason_1", StringType(), True),
        StructField("decline_reason_2", StringType(), True),
        StructField("decline_reason_3", StringType(), True)
    ])

    return spark.createDataFrame(sample_loan_application_data, schema)


@pytest.fixture
def mock_dynamodb_resource():
    """Mock DynamoDB resource for testing"""
    with mock_dynamodb():
        # Create mock DynamoDB table
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

        # Create a test table
        table = dynamodb.create_table(
            TableName='test_table',
            KeySchema=[
                {'AttributeName': 'pk', 'KeyType': 'HASH'},
                {'AttributeName': 'sk', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'pk', 'AttributeType': 'S'},
                {'AttributeName': 'sk', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )

        yield dynamodb


@pytest.fixture
def sample_parquet_file(tmp_path, spark, loan_application_df):
    """Create a sample parquet file for testing"""
    file_path = tmp_path / "test_data.parquet"
    loan_application_df.write.parquet(str(file_path))
    return file_path


@pytest.fixture
def sample_domain_error():
    """Sample domain error for testing"""
    return DomainError(
        DomainCode.DYNAMODB_WRITE_FAILURE,
        failed_count=5,
        total_count=100,
        table_name="test_table",
        data_type="LOAN_APPLICATION"
    )