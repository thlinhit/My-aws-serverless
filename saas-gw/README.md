# SaaS Gateway API

A multi-tenant serverless API gateway built with AWS API Gateway, Lambda, and CloudFront using the Serverless Framework.

## Features

- Partner-specific API endpoints
- Lambda Authorizer that extracts `partnerId` from URL path
- API Key authentication
- CloudFront distribution for global content delivery
- Python 3.12 runtime

## Architecture

The API uses a Lambda Authorizer to extract the partner ID from the API path and inject it into the request context. This allows downstream Lambda functions to know which partner/tenant is making the request without having to parse the path themselves.

```
Client --> CloudFront --> API Gateway --> Lambda Authorizer --> Lambda Function
```

The authorizer extracts the partner ID from paths like:
- `/api/abc/hello` → partner: abc
- `/api/tymebank/hello` → partner: tymebank
- `/api/sanlam/hello` → partner: sanlam

## Prerequisites

- Node.js 14+
- Serverless Framework v3
- AWS CLI configured with appropriate credentials
- Python 3.12

## Setup

1. Install dependencies:

```bash
npm install
```

2. Install Python requirements plugin:

```bash
npm install serverless-python-requirements --save-dev
```

## Deployment

Deploy to the default stage (dev):

```bash
npm run deploy
```

After deployment, you'll receive the CloudFront domain name and API key.

## Testing

1. Set your API key and CloudFront domain in the test_api.sh script:

```bash
# Edit test_api.sh
API_KEY="your-api-key"
CF_DOMAIN="your-cloudfront-domain"
```

2. Run the test script:

```bash
./test_partners.sh
```

You can also test the authorizer locally:

```bash
python test_authorizer.py
```

And test the hello handler:

```bash
python test_hello.py
```

## Folder Structure

```
├── serverless.yml          # Serverless Framework configuration
├── src/
│   └── handlers/
│       ├── authorizer.py   # Lambda Authorizer
│       └── hello.py        # Example Lambda Function
├── test_api.sh             # API test script
├── test_authorizer.py      # Authorizer test script
└── test_hello.py           # Hello handler test script
```

## Customization

To add more endpoints:

1. Add a new Lambda function in the `src/handlers/` directory
2. Update the `serverless.yml` file to include the new function and its endpoints
3. Configure the endpoints with the authorizer

## Troubleshooting

- If you receive 401 Unauthorized errors, ensure you're including the `x-api-key` header with your API key
- Check CloudWatch Logs for detailed error messages from the Lambda functions
- Verify that the CloudFront distribution is configured to forward the necessary headers (x-api-key, Authorization, etc.)
- Test directly against the API Gateway endpoint to isolate CloudFront-related issues