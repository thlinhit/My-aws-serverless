import json
import logging
import re

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """
    Handler function for API endpoints
    Supports multiple partner paths:
    - /api/abc/hello (original)
    - /api/tymebank/* (Tymebank)
    - /api/sanlam/* (Sanlam)
    
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
    
    # Get partnerId from the authorizer context
    # This will be available if the request went through our authorizer
    # Otherwise fall back to extracting from path
    partner_id = "default"
    
    # Try to get partnerId from authorizer context
    if 'requestContext' in event and 'authorizer' in event['requestContext']:
        authorizer_context = event['requestContext']['authorizer']
        # Check if partnerId is in the authorizer context
        if 'partnerId' in authorizer_context:
            partner_id = authorizer_context['partnerId']
            logger.info(f"Using partnerId from authorizer context: {partner_id}")

    
    logger.info(f"Request from partner: {partner_id}")
    
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
            "partnerId": partner_id
        })
    }
    
    return response 