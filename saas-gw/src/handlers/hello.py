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
    
    # Determine which partner is calling (if any)
    partner = "default"
    
    # Check if this is a partner-specific path
    tymebank_pattern = r'^/api/tymebank.*'
    sanlam_pattern = r'^/api/sanlam.*'
    
    if re.match(tymebank_pattern, path):
        partner = "tymebank"
    elif re.match(sanlam_pattern, path):
        partner = "sanlam"
    
    logger.info(f"Request from partner: {partner}")
    
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
            "partner": partner
        })
    }
    
    return response 