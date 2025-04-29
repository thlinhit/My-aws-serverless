import json
import logging
import re
import os
import traceback
import boto3
from botocore.exceptions import ClientError

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize SSM client
ssm = boto3.client('ssm')

def handler(event, context):
    """
    Lambda authorizer that extracts partnerId from the API path
    and validates the API key against the partner-specific key stored in SSM.
    """
    try:
        logger.info("Authorizer event: %s", json.dumps(event))
        
        # Extract the path from the event
        path = ""
        
        # First try direct path from event
        if 'path' in event:
            path = event.get('path')
        # Then try from resource
        elif 'resource' in event:
            path = event.get('resource')
        # Then try from requestContext
        elif 'requestContext' in event and 'path' in event['requestContext']:
            path = event['requestContext']['path']
        
        logger.info(f"Extracted path: {path}")
        
        # Extract partnerId from path using regex
        partner_id = "default"  # Default fallback
        
        # Try to get partnerId from the X-Partner-Id header first (set by CloudFront)
        headers = event.get('headers', {}) or {}
        if headers and 'X-Partner-Id' in headers:
            partner_id = headers['X-Partner-Id']
            logger.info(f"Using partnerId from header: {partner_id}")
        # Fall back to extracting from path if header is not present
        elif path:
            path_match = re.search(r'/api/([^/]+)/.*', path)
            if path_match:
                partner_id = path_match.group(1)
                logger.info(f"Extracted partnerId from path: {partner_id}")
        
        # Get the API key from the request
        api_key = None
        if headers and 'X-Api-Key' in headers:
            api_key = headers['X-Api-Key']
        
        # Construct methodArn if it doesn't exist
        method_arn = event.get('methodArn', '')
        if not method_arn and 'requestContext' in event:
            rc = event['requestContext']
            # Format: arn:aws:execute-api:region:account-id:api-id/stage/method/resource-path
            if all(k in rc for k in ['accountId', 'apiId', 'stage', 'httpMethod']):
                region = os.environ.get('AWS_REGION', 'us-east-1')
                resource_path = path.lstrip('/')
                method_arn = f"arn:aws:execute-api:{region}:{rc['accountId']}:{rc['apiId']}/{rc['stage']}/{rc['httpMethod']}/{resource_path}"
                logger.info(f"Constructed methodArn: {method_arn}")
        
        # For cases where we still don't have a methodArn, create a default one
        if not method_arn:
            logger.warning("No methodArn available, creating a default one")
            region = os.environ.get('AWS_REGION', 'us-east-1')
            method_arn = f"arn:aws:execute-api:{region}:*:*/*/*"
        
        # Validate API key against partner-specific key in SSM
        if api_key and partner_id != "default":
            effect = validate_partner_api_key(partner_id, api_key)
        else:
            logger.warning(f"Missing API key or partner ID. API key present: {api_key is not None}, Partner ID: {partner_id}")
            effect = 'Deny'
        
        # Generate policy based on validation result
        policy = generate_policy('user', 'Allow', method_arn, partner_id)
        logger.info(f"Generated policy with effect: {effect}")
        
        return policy
    except Exception as e:
        logger.error(f"Error in authorizer: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Deny access on errors to be safe
        emergency_policy = {
            'principalId': 'user',
            'policyDocument': {
                'Version': '2012-10-17',
                'Statement': [
                    {
                        'Action': 'execute-api:Invoke',
                        'Effect': 'Deny',
                        'Resource': '*'
                    }
                ]
            },
            'context': {
                'partnerId': 'default',
                'error': str(e)
            }
        }
        return emergency_policy

def validate_partner_api_key(partner_id, api_key):
    """
    Validate the API key against the partner-specific key stored in SSM.
    
    Parameters:
    - partner_id: The ID of the partner
    - api_key: The API key from the request
    
    Returns:
    - 'Allow' if the API key is valid, 'Deny' otherwise
    """
    try:
        # Construct the SSM parameter name with leading slash
        ssm_param_name = f"/saas/apikey/{partner_id}"
        
        # Get the parameter from SSM
        response = ssm.get_parameter(
            Name=ssm_param_name,
            WithDecryption=True  # Decrypt the parameter if it's encrypted
        )
        
        # Get the stored API key
        stored_api_key = response['Parameter']['Value']
        
        # Compare the API keys
        if api_key == stored_api_key:
            logger.info(f"API key validation successful for partner: {partner_id}")
            return 'Allow'
        else:
            logger.warning(f"API key validation failed for partner: {partner_id}")
            return 'Deny'
    
    except ClientError as e:
        if e.response['Error']['Code'] == 'ParameterNotFound':
            logger.error(f"SSM parameter not found for partner: {partner_id}")
        else:
            logger.error(f"Error retrieving SSM parameter: {str(e)}")
        return 'Deny'
    
    except Exception as e:
        logger.error(f"Unexpected error validating API key: {str(e)}")
        return 'Deny'

def generate_policy(principal_id, effect, resource, partner_id):
    """
    Generate IAM policy document with custom context
    """
    policy = {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': '*'
                }
            ]
        },
        # Custom context with partnerId
        'context': {
            'partnerId': partner_id
        }
    }
    
    return policy