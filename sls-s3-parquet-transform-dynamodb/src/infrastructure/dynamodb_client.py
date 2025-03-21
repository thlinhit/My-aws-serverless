import os
from dataclasses import dataclass
from typing import Dict, List, Any, Tuple

import boto3
from boto3.dynamodb.types import TypeSerializer
from pyspark.sql import Row

from infrastructure.logger import logger
from botocore.config import Config as BotoCfg

DYNAMO_DB_SERVICE = "dynamodb"
REGION = os.getenv("TABLE_REGION", "eu-west-1")


@dataclass
class DynamoDBWriteResult:
    """
    Result of a DynamoDB write operation.
    Contains information about success and error counts.
    """
    success_count: int = 0
    error_count: int = 0
    errors: List[str] = None
    failed_items: List[Dict[str, Any]] = None


class DynamoDBClient:
    """
    Client for handling DynamoDB operations.
    This class encapsulates all DynamoDB-specific logic and infrastructure concerns.
    """
    
    def __init__(self, region: str):
        """
        Initialize DynamoDB client.
        
        Args:
            region: AWS region
        """
        self.region = region
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.serializer = TypeSerializer()

    @staticmethod
    def _convert_row_to_dict(row: Row) -> Dict[str, Any]:
        """
        Convert a Spark Row to a dictionary.
        
        Args:
            row: Spark Row object
            
        Returns:
            Dictionary representation of the row
        """
        if isinstance(row, Row):
            return row.asDict()
        return dict(row)

    @staticmethod
    def write_partition_to_dynamodb(partition, table_name: str):
        """
        Process a partition of data and write it to DynamoDB.
        
        Args:
            partition: Iterator of rows to process
            table_name: Name of the DynamoDB table
            region: AWS region
            
        Returns:
            DynamoDBWriteResult containing success/error counts and failed items
        """
        result = DynamoDBWriteResult(
            success_count=0,
            error_count=0,
            errors=[],
            failed_items=[]
        )
        
        try:
            table = DynamoDBClient.get_boto3_resource().Table(table_name)
            
            with table.batch_writer() as batch:
                for row in partition:
                    try:
                        item = DynamoDBClient._convert_row_to_dict(row)["dynamodb_item"]
                        batch.put_item(Item=item)
                        result.success_count += 1
                    except Exception as e:
                        result.error_count += 1
                        error_msg = str(e)
                        result.errors.append(error_msg)
                        result.failed_items.append({
                            "item": item,
                            "error": error_msg
                        })
                        logger.error(
                            f"Error writing item to DynamoDB: {error_msg}",
                            extra={
                                "table_name": table_name,
                                "error": error_msg,
                                "row": str(row)
                            }
                        )
        except Exception as e:
            error_msg = str(e)
            result.errors.append(error_msg)
            logger.error(
                f"Error with batch writer: {error_msg}",
                extra={
                    "table_name": table_name,
                    "error": error_msg
                }
            )
        
        return result

    @staticmethod
    def get_boto3_resource():
        IS_LOCAL = os.environ.get("RUNNING_STAGE", "local") == "local"
        if IS_LOCAL:
            return boto3.resource(
                DYNAMO_DB_SERVICE,
                endpoint_url="http://localhost:8000",
                region_name="localhost",
                aws_access_key_id='dummy',
                aws_secret_access_key='dummy',
            )
        else:
            return boto3.resource(
                DYNAMO_DB_SERVICE,
                region_name=REGION,
                config=BotoCfg(retries={"mode": "standard"}),
            )
