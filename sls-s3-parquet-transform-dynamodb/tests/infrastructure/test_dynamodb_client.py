"""
Tests for the DynamoDB client
"""
import os
import boto3
import pytest
from unittest.mock import MagicMock, patch
from pyspark.sql import Row
from moto import mock_dynamodb  # modern Moto version

from infrastructure.dynamodb_client import DynamoDBClient, DynamoDBWriteResult


@pytest.fixture(scope="function")
def aws_credentials():
    """Set up dummy AWS credentials for moto"""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    yield
    for var in [
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_SECURITY_TOKEN",
        "AWS_SESSION_TOKEN",
        "AWS_DEFAULT_REGION",
    ]:
        os.environ.pop(var, None)


@pytest.fixture
def mock_dynamodb_resource(aws_credentials):
    with mock_dynamodb():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        yield dynamodb


@pytest.fixture
def mock_dynamodb_table(mock_dynamodb_resource):
    table = mock_dynamodb_resource.create_table(
        TableName="test_table",
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    return table


@pytest.fixture
def client(mock_dynamodb_resource, mock_dynamodb_table):
    """Create a DynamoDB client with mocked resource"""
    with patch("infrastructure.dynamodb_client.boto3.resource", return_value=mock_dynamodb_resource):
        yield DynamoDBClient(region="us-east-1")


class TestDynamoDBClient:
    def test_convert_row_to_dict(self):
        """Test converting a Spark Row to a dictionary"""
        row = Row(id=1, name="Test")
        result = DynamoDBClient._convert_row_to_dict(row)
        assert isinstance(result, dict)
        assert result["id"] == 1
        assert result["name"] == "Test"

    def test_write_partition_to_dynamodb_success(self, client):
        """Test writing a partition to DynamoDB successfully"""
        partition = [
            {"dynamodb_item": {"pk": "CUS#12345", "sk": "LOAN_APP#APP001", "data": "test1"}},
            {"dynamodb_item": {"pk": "CUS#67890", "sk": "LOAN_APP#APP002", "data": "test2"}},
        ]

        result = client.write_partition_to_dynamodb(partition, table_name="test_table")

        assert isinstance(result, DynamoDBWriteResult)
        assert result.success_count == 2
        assert result.error_count == 0
        assert not result.errors
        assert not result.failed_items

    def test_write_partition_to_dynamodb_with_errors(self, client):
        """Test writing a partition to DynamoDB with one simulated error"""
        partition = [
            {"dynamodb_item": {"pk": "CUS#12345", "sk": "LOAN_APP#APP001", "data": "test1"}},
            {"dynamodb_item": {"pk": "CUS#67890", "data": "test2"}},
        ]

        mock_batch_writer = MagicMock()
        mock_batch_writer.put_item.side_effect = [None, Exception("Simulated error")]

        mock_table = MagicMock()
        mock_table.batch_writer.return_value.__enter__.return_value = mock_batch_writer

        with patch.object(client, "dynamodb") as mock_dynamodb:
            mock_dynamodb.Table.return_value = mock_table
            result = client.write_partition_to_dynamodb(partition, table_name="test_table")

        assert isinstance(result, DynamoDBWriteResult)
        assert result.success_count == 1
        assert result.error_count == 1
        assert len(result.errors) == 1
        assert len(result.failed_items) == 1
        assert result.failed_items[0]["item"]["pk"] == "CUS#67890"