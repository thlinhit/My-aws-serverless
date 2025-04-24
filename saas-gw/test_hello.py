import json
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from handlers.hello import handler as hello_handler

def test_hello_handler():
    # Test cases with different authorizer contexts
    test_cases = [
        {
            'name': 'With ABC authorizer context',
            'event': {
                'path': '/api/abc/hello',
                'requestContext': {
                    'authorizer': {
                        'partnerId': 'abc'
                    }
                }
            },
            'expected_partner_id': 'abc'
        },
        {
            'name': 'With TymeBank authorizer context',
            'event': {
                'path': '/api/tymebank/hello',
                'requestContext': {
                    'authorizer': {
                        'partnerId': 'tymebank'
                    }
                }
            },
            'expected_partner_id': 'tymebank'
        },
        {
            'name': 'Without authorizer context (fallback to path)',
            'event': {
                'path': '/api/sanlam/hello',
                # No authorizer context
            },
            'expected_partner_id': 'sanlam'
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest Case {i+1}: {test_case['name']}")
        
        # Call the hello handler
        result = hello_handler(test_case['event'], {})
        
        # Parse the response body
        response_body = json.loads(result['body'])
        print(f"Response: {json.dumps(response_body, indent=2)}")
        
        # Verify the partnerId
        actual_partner_id = response_body['partnerId']
        expected_partner_id = test_case['expected_partner_id']
        
        if actual_partner_id == expected_partner_id:
            print(f"✅ PASS: partnerId is '{actual_partner_id}' as expected")
        else:
            print(f"❌ FAIL: partnerId is '{actual_partner_id}', expected '{expected_partner_id}'")

if __name__ == '__main__':
    test_hello_handler() 