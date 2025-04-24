import json
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from handlers.authorizer import handler as authorizer_handler

def test_authorizer():
    # Test cases for different paths and event structures
    test_cases = [
        {
            'name': 'Standard request with path',
            'event': {
                'type': 'REQUEST',
                'methodArn': 'arn:aws:execute-api:us-east-1:123456789012:abcdef123/dev/POST/api/abc/hello',
                'path': '/api/abc/hello',
                'headers': {
                    'x-api-key': 'test-api-key'
                }
            },
            'expected_partner_id': 'abc'
        },
        {
            'name': 'Request with path in methodArn only',
            'event': {
                'type': 'REQUEST',
                'methodArn': 'arn:aws:execute-api:us-east-1:123456789012:abcdef123/dev/POST/api/tymebank/hello',
                # No path provided
                'headers': {
                    'x-api-key': 'test-api-key'
                }
            },
            'expected_partner_id': 'tymebank'
        },
        {
            'name': 'Request with path in requestContext',
            'event': {
                'type': 'REQUEST',
                'methodArn': 'arn:aws:execute-api:us-east-1:123456789012:abcdef123/dev/POST/api/sanlam/hello',
                'requestContext': {
                    'path': '/api/sanlam/hello'
                },
                'headers': {
                    'x-api-key': 'test-api-key'
                }
            },
            'expected_partner_id': 'sanlam'
        },
        {
            'name': 'Request with pathParameters',
            'event': {
                'type': 'REQUEST',
                'methodArn': 'arn:aws:execute-api:us-east-1:123456789012:abcdef123/dev/POST/api/abc/hello',
                'pathParameters': {
                    'proxy': 'api/abc/hello'
                },
                'headers': {
                    'x-api-key': 'test-api-key'
                }
            },
            'expected_partner_id': 'abc'
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest Case {i+1}: {test_case['name']}")
        
        # Call the authorizer
        result = authorizer_handler(test_case['event'], {})
        
        # Print the result
        print(f"Result: {json.dumps(result, indent=2)}")
        
        # Verify the partnerId
        actual_partner_id = result['context']['partnerId']
        expected_partner_id = test_case['expected_partner_id']
        
        if actual_partner_id == expected_partner_id:
            print(f"✅ PASS: partnerId is '{actual_partner_id}' as expected")
        else:
            print(f"❌ FAIL: partnerId is '{actual_partner_id}', expected '{expected_partner_id}'")
        
        # Verify the resource in the policy
        resource = result['policyDocument']['Statement'][0]['Resource']
        print(f"Resource: {resource}")
        # Check if the resource is a wildcard ending with /*
        if resource.endswith('/*'):
            print("✅ PASS: Resource is properly wildcarded")
        else:
            print("❓ NOTE: Resource is not wildcarded, might be restrictive")

if __name__ == '__main__':
    test_authorizer() 