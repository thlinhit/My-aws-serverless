import json
import logging
import re
import os
import traceback

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """
    Lambda authorizer that extracts partnerId from the API path
    and returns it as part of the authorization context.
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
        if path:
            path_match = re.search(r'/api/([^/]+)/.*', path)
            if path_match:
                partner_id = path_match.group(1)
        
        logger.info(f"Extracted partnerId: {partner_id}")
        
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
        
        # Always generate Allow policy
        policy = generate_policy('user', 'Allow', method_arn, partner_id)
        logger.info(f"Generated policy: {json.dumps(policy)}")
        
        return policy
    except Exception as e:
        logger.error(f"Error in authorizer: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Always return an allow policy in case of errors
        # This ensures your API doesn't get blocked due to authorizer issues
        emergency_policy = {
            'principalId': 'user',
            'policyDocument': {
                'Version': '2012-10-17',
                'Statement': [
                    {
                        'Action': 'execute-api:Invoke',
                        'Effect': 'Allow',
                        'Resource': '*'
                    }
                ]
            },
            'context': {
                'partnerId': 'default'
            }
        }
        return emergency_policy

def generate_policy(principal_id, effect, resource, partner_id):
    """
    Generate IAM policy document with custom context
    """
    # Always use wildcard resource to be most permissive
    wildcard_resource = "*"
    
    policy = {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': wildcard_resource
                }
            ]
        },
        # Custom context with partnerId
        'context': {
            'partnerId': partner_id
        }
    }
    
    return policy