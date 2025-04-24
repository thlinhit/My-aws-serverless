import json
import logging
import re

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """
    Lambda authorizer that extracts partnerId from the API path
    and returns it as part of the authorization context.
    
    Parameters:
    - event: API Gateway Lambda Authorizer Input Format
    - context: Lambda Context Runtime Methods and Attributes
    
    Returns:
    - API Gateway Lambda Authorizer Output Format with custom context
    """
    logger.info("Authorizer event: %s", json.dumps(event))
    
    # Get the ARN of the API Gateway API from the methodArn
    method_arn = event.get('methodArn', '')
    
    # Extract API path from the request context
    path = event.get('path', '')
    
    # For request authorizers, path might be in different locations
    if not path and event.get('resource'):
        path = event.get('resource')
    
    # Check if we can extract it from the path parameters
    if not path and 'pathParameters' in event and event['pathParameters']:
        # Reconstruct from pathParameters
        path_parts = []
        if 'proxy' in event['pathParameters']:
            path_parts.append(event['pathParameters']['proxy'])
        path = '/' + '/'.join(path_parts)
    
    # Try to get it from requestContext
    if not path and 'requestContext' in event:
        path = event.get('requestContext', {}).get('path', '')
    
    # Get path from methodArn as a last resort
    if not path and method_arn:
        # Extract resource path from methodArn (format: arn:aws:execute-api:region:account-id:api-id/stage/method/resource-path)
        # E.g., arn:aws:execute-api:us-east-1:123456789012:api-id/dev/POST/api/abc/hello
        path_match = re.search(r'arn:aws:execute-api:[^:]+:[^:]+:[^/]+/[^/]+/[^/]+/(.+)', method_arn)
        if path_match:
            path = '/' + path_match.group(1)
    
    logger.info(f"Processing authorization for path: {path}")
    
    # Extract partnerId from path using regex
    partner_id = "unknown"
    path_match = re.search(r'/api/([^/]+)/.*', path)
    if path_match:
        partner_id = path_match.group(1)
    
    logger.info(f"Extracted partnerId: {partner_id}")

    # Always allow access - authorization will be handled by API key
    # The authorizer is only used to add the partnerId to the context
    policy = generate_policy('user', 'Allow', method_arn, partner_id)
    
    return policy

def generate_policy(principal_id, effect, resource, partner_id):
    """
    Generate IAM policy document with custom context
    
    Parameters:
    - principal_id: The principal ID (user identifier)
    - effect: Allow or Deny
    - resource: The resource ARN
    - partner_id: Partner ID extracted from the path
    
    Returns:
    - Policy document with custom context
    """
    # For API Gateway, we need to generate a wildcard resource when authorizing
    # This ensures the policy applies to all resources under the API
    if resource:
        # Extract the base part of the resource ARN (without the specific method and path)
        # e.g., arn:aws:execute-api:region:account-id:api-id/stage
        resource_parts = resource.split('/')
        if len(resource_parts) >= 3:
            # Keep the base and append a wildcard
            base_resource = '/'.join(resource_parts[0:3])
            wildcard_resource = f"{base_resource}/*"
        else:
            wildcard_resource = resource
    else:
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
        # Custom context that will be available in the Lambda function
        'context': {
            'partnerId': partner_id
        }
    }
    
    return policy 