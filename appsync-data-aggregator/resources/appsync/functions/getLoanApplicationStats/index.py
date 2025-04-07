import json
import os
import boto3
from typing import Dict, Any
from aws_lambda_powertools.utilities.typing import LambdaContext
from decimal import Decimal
from functions.shared.infrastructure.logger import logger
from functions.shared.exception.domain_code import DomainCode, DomainError

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')

class DecimalEncoder(json.JSONEncoder):
    """Helper class to convert Decimal types to float for JSON serialization"""
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o) if o % 1 else int(o)
        return super().default(o)

@logger.inject_lambda_context(log_event=True)
def handler(event: Dict[Any, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    Queries loan applications for a specific customer and calculates:
    - Sum of requested_amount for declined applications
    - Sum of accepted_amount for approved applications
    
    Args:
        event: Contains customerId to filter results
        
    Returns:
        Dict with totalDeclinedAmount and totalApprovedAmount
    """
    # Get the table name from environment variables
    table_name = os.environ.get('DYNAMODB_TABLE')
    table = dynamodb.Table(table_name)
    
    # Get the customerId (now required)
    customer_id = event['customerId']
    
    try:
        # Query for the specific customer's applications
        logger.info(f"Querying table {table_name} for customer {customer_id}")
        
        # Use scan with a filter expression to get all applications for this customer
        response = table.scan(
            FilterExpression="customer_id = :cid",
            ExpressionAttributeValues={
                ":cid": customer_id
            }
        )
        items = response.get('Items', [])
        
        # Continue scanning if we exceed the limit
        while 'LastEvaluatedKey' in response:
            response = table.scan(
                FilterExpression="customer_id = :cid",
                ExpressionAttributeValues={
                    ":cid": customer_id
                },
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            items.extend(response.get('Items', []))
        
        logger.info(f"Retrieved {len(items)} loan application(s) for customer {customer_id}")
        
        # Calculate sums for different statuses
        total_declined_amount = sum(
            float(item.get('requested_amount', 0)) 
            for item in items 
            if item.get('status', '').lower() == 'declined'
        )
        
        total_approved_amount = sum(
            float(item.get('accepted_amount', 0)) 
            for item in items 
            if item.get('status', '').lower() == 'approved'
        )
        
        result = {
            "totalDeclinedAmount": total_declined_amount,
            "totalApprovedAmount": total_approved_amount
        }
        
        logger.info(f"Calculated statistics for customer {customer_id}: {result}")
        return result
        
    except Exception as e:
        logger.exception(
            "Unexpected error occurred, customerId: {customer_id}",
            extra={
                "error_message": str(e),
            }
        )
        raise DomainError(DomainCode.UNKNOWN, error_message=str(e))
