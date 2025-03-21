from dataclasses import dataclass
from typing import Dict, List, Any, Tuple

import boto3
from boto3.dynamodb.types import TypeSerializer

from infrastructure.logger import logger


@dataclass
class DynamoDBWriteResult:
    """
    Result of a DynamoDB write operation.
    Contains information about success and error counts.
    """
    success_count: int = 0
    error_count: int = 0
    errors: List[str] = None


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
    
    def process_partition_to_dynamodb(
        self,
        partition: List[Dict[str, Any]],
        table_name: str,
    ) -> Tuple[int, int]:
        success_count = 0
        error_count = 0
        
        table = self.dynamodb.Table(table_name)
        
        try:
            with table.batch_writer() as batch:
                for item in partition:
                    try:
                        batch.put_item(Item=item)
                        success_count += 1
                    except Exception as e:
                        error_count += 1
                        logger.error(
                            f"Error writing item to DynamoDB: {str(e)}",
                            extra={
                                "table_name": table_name,
                                "error": str(e)
                            }
                        )
        except Exception as e:
            logger.error(
                f"Error with batch writer: {str(e)}",
                extra={
                    "table_name": table_name,
                    "error": str(e)
                }
            )
        
        return success_count, error_count