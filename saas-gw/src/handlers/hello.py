import json
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """
    Handler function for the /api/abc/hello endpoint
    
    Parameters:
    - event: API Gateway Lambda Proxy Input Format
    - context: Lambda Context Runtime Methods and Attributes
    
    Returns:
    - API Gateway Lambda Proxy Output Format
    """
    logger.info("Processing request to /api/abc/hello")
    
    # Log the incoming event for debugging
    logger.info(f"Event: {json.dumps(event)}")
    
    # Create response
    response = {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",  # For CORS support
            "Access-Control-Allow-Credentials": True
        },
        "body": json.dumps({"message": "HELLO"})
    }
    
    return response 