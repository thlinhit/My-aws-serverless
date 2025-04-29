import json
import logging
import re

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """
    Handler function for API endpoints
    Supports dynamic partner paths:
    - /api/hello (generic endpoint)
    - /api/{partnerId}/hello (partner-specific, rewritten by CloudFront)
    
    The partner ID is extracted by CloudFront and passed in the x-partner-id header
    
    Parameters:
    - event: API Gateway Lambda Proxy Input Format
    - context: Lambda Context Runtime Methods and Attributes
    
    Returns:
    - API Gateway Lambda Proxy Output Format
    """
    # Extract path for logging and partner identification
    path = event.get('path', '')
    logger.info(f"Processing request to {path}")
    
    # Log the incoming event for debugging
    logger.info(f"Event: {json.dumps(event)}")
    
    # Get partnerId from various sources with priority:
    # 1. From the x-partner-id header (set by CloudFront)
    # 2. From the authorizer context (set by authorizer Lambda)
    # 3. Default fallback value
    partner_id = "default"
    
    # Try to get partnerId from x-partner-id header (set by CloudFront)
    headers = event.get('headers', {}) or {}
    if headers and 'X-Partner-Id' in headers:
        partner_id = headers['X-Partner-Id']
        logger.info(f"Using partnerId from x-partner-id header: {partner_id}")
    # If not in header, try authorizer context
    elif 'requestContext' in event and 'authorizer' in event['requestContext']:
        authorizer_context = event['requestContext']['authorizer']
        if 'partnerId' in authorizer_context:
            partner_id = authorizer_context['partnerId']
            logger.info(f"Using partnerId from authorizer context: {partner_id}")
    
    logger.info(f"Request from partner: {partner_id}")
    
    # Get original path from headers if CloudFront rewrite occurred
    original_path = path
    if headers and 'X-Original-Path' in headers:
        original_path = headers['X-Original-Path']
        logger.info(f"Original path from CloudFront: {original_path}")
    
    # Create response with partner information
    response = {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",  # For CORS support
            "Access-Control-Allow-Credentials": True
        },

        "body": json.dumps({
            "message": "HELLO",
            "partnerId": partner_id,
            "path": path,
            "originalPath": original_path
        })
    }
    
    return response 