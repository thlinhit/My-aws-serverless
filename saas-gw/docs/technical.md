# Technical Documentation - API Gateway Service

## Development Environment

### Required Tools
- Node.js (v14+)
- npm (v6+) or yarn
- AWS CLI (v2+)
- Serverless Framework (v3.x)
- Python 3.12

### AWS Account Setup
1. AWS Account with appropriate IAM permissions
2. AWS CLI configured with access credentials
3. Profile setup for deployment (e.g., `AWS_PROFILE=tx-sandbox`)

### Local Development Setup
1. Clone repository
2. Run `npm install` to install dependencies
3. Configure AWS credentials and profile

## Technical Stack

### Infrastructure
- **AWS API Gateway**: Handles API requests, authentication, and routing
- **AWS Lambda**: Executes serverless functions
- **AWS CloudWatch**: Provides logging and monitoring
- **AWS CloudFormation**: Creates and manages AWS resources (via Serverless Framework)
- **AWS IAM**: Manages permissions and access control

### Development Tools
- **Serverless Framework v3**: Infrastructure as code and deployment management
- **serverless-python-requirements**: Plugin for managing Python dependencies
- **npm**: Package management and script execution

### Runtime Environment
- **AWS Lambda Python Runtime**: Python 3.12
- **AWS Lambda Execution Environment**: Amazon Linux 2

## Code Structure

```
.
├── src/
│   └── handlers/
│       └── hello.py      # Lambda handler for the hello endpoint
├── docs/                 # Project documentation
├── tasks/                # Task tracking and active context
├── serverless.yml        # Serverless Framework configuration
├── requirements.txt      # Python dependencies
├── package.json          # npm dependencies and scripts
└── README.md             # Project overview and usage
```

## Configuration Details

### serverless.yml
The `serverless.yml` file contains all the configuration needed for the Serverless Framework to deploy our application:

```yaml
service: saas-gw-api

frameworkVersion: '3'

provider:
  name: aws
  runtime: python3.12
  stage: ${opt:stage, 'dev'}
  region: us-east-1
  apiGateway:
    apiKeys:
      - name: ${self:service}-${self:provider.stage}-apikey
        enabled: true
  environment:
    STAGE: ${self:provider.stage}

functions:
  hello:
    handler: src/handlers/hello.handler
    events:
      - http:
          path: api/abc/hello
          method: post
          private: true  # Requires API key
          cors: true

plugins:
  - serverless-python-requirements

package:
  individually: true
  patterns:
    - '!node_modules/**'
    - '!.gitignore'
    - '!.git/**'
    - '!.pytest_cache/**'
    - '!tests/**'
```

### Lambda Handler
The Lambda handler is defined in `src/handlers/hello.py`:

```python
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
```

### NPM Scripts
Defined in `package.json` for common operations:

```json
{
  "scripts": {
    "deploy": "AWS_PROFILE=tx-sandbox sls deploy --stage dev",
    "remove": "serverless remove"
  }
}
```

## Design Patterns and Decisions

### API Gateway Configuration
- **API Keys**: Used for authentication to secure the API
- **CORS Support**: Enabled to allow browser-based applications to call the API
- **Proxy Integration**: Using Lambda proxy integration for simplified request/response handling

### Lambda Function Design
- **Logging**: Using Python's logging module with JSON formatting for structured logs
- **Error Handling**: Proper error handling with appropriate HTTP status codes
- **Response Formatting**: Consistent response format with appropriate headers

### Deployment Strategy
- **Environment Isolation**: Using stages to separate different environments
- **AWS Profile Usage**: Using AWS profiles to manage multiple deployment targets
- **Optimized Packaging**: Excluding unnecessary files to reduce package size

## Security Considerations

### API Authentication
- API Gateway API Keys for request authentication
- Private endpoints requiring API key authentication

### IAM Permissions
- Least privilege permissions for Lambda execution roles
- Automatically managed by Serverless Framework

### Data Security
- HTTPS for all API communications
- No sensitive data stored in the Lambda function

## Performance Considerations

### Lambda Function
- Small deployment package for faster cold starts
- Minimal dependencies to reduce startup time
- Efficient logging to minimize overhead

### API Gateway
- CORS configured to enable browser-based applications
- Appropriate timeouts to handle varying request loads

## Testing Approaches

### Local Testing
- Invoke Lambda functions locally with Serverless Framework
- Test API endpoints with Postman or curl

### Deployment Testing
- Deploy to a development environment before production
- Test with real API Gateway and Lambda execution

## Troubleshooting

### Common Issues
- API Gateway 403 errors: Check API key configuration
- Lambda execution errors: Check CloudWatch logs
- Deployment failures: Check IAM permissions and CloudFormation events

### Logging and Monitoring
- CloudWatch logs for API Gateway and Lambda
- CloudWatch metrics for performance monitoring

## Future Technical Considerations

### CI/CD Integration
- Automated testing and deployment pipeline
- Environment promotion strategy

### Enhanced Monitoring
- CloudWatch dashboards and alarms
- X-Ray tracing for performance analysis

### Additional Features
- Authentication enhancements with OAuth or Cognito
- API documentation with Swagger/OpenAPI
- Rate limiting and quota management 