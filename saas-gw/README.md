# API Gateway with Lambda Backend

This project provisions an AWS API Gateway with a Lambda function backend using Serverless Framework v3, now fronted by CloudFront for improved performance and additional capabilities.

## Features

- API Gateway endpoint at `api/abc/hello` (POST method)
- API key authentication required
- Python 3.12 Lambda function backend
- Returns a simple "HELLO" response
- CloudFront distribution for improved performance and global reach

## Prerequisites

- Node.js (v14+)
- npm or yarn
- AWS CLI configured with appropriate credentials
- Serverless Framework installed (`npm install -g serverless`)

## Installation

1. Clone this repository
2. Install dependencies:

```bash
npm install
```

## Deployment

To deploy to the development environment:

```bash
npm run deploy
```

To deploy to production:

```bash
npm run deploy:prod
```

For verbose deployment logs:

```bash
npm run deploy:verbose
```

## CloudFront Distribution

After deployment, you can retrieve your CloudFront domain name by running:

```bash
npm run cloudfront:info
```

This will display the CloudFront domain name that you can use to access your API.

## Authentication

After deployment, you can find your API key in the AWS Console under API Gateway > API Keys, or by running:

```bash
aws apigateway get-api-keys --name-query "saas-gw-api-dev-apikey" --include-values
```

## Usage

### Via API Gateway (Direct)

To test the API directly through API Gateway, use curl or any API client with your API key:

```bash
curl -X POST https://your-api-id.execute-api.us-east-1.amazonaws.com/dev/api/abc/hello \
  -H "x-api-key: your-api-key" \
  -H "Content-Type: application/json"
```

### Via CloudFront

To access the API through CloudFront, use the CloudFront domain name:

```bash
curl -X POST https://your-cloudfront-domain.cloudfront.net/api/abc/hello \
  -H "x-api-key: your-api-key" \
  -H "Content-Type: application/json"
```

The response should be:

```json
{
  "message": "HELLO"
}
```

## Benefits of CloudFront

- **Improved Performance**: Content is cached at edge locations closer to users
- **Reduced Latency**: Faster response times for global users
- **Cost Savings**: Reduced data transfer costs from your origin server
- **DDoS Protection**: Built-in protection against certain attacks
- **SSL/TLS**: Managed HTTPS certificates and encryption
- **Custom Domain Support**: Ability to use your own domain name (future enhancement)

## Partner-Specific Endpoints

This API supports partner-specific endpoints through CloudFront path patterns:

1. **Tymebank**:
   ```
   https://your-cloudfront-domain.cloudfront.net/api/tymebank/hello
   ```

2. **Sanlam**:
   ```
   https://your-cloudfront-domain.cloudfront.net/api/sanlam/hello
   ```

3. **Default path** (original):
   ```
   https://your-cloudfront-domain.cloudfront.net/api/abc/hello
   ```

All paths route to the same Lambda function, which identifies the partner based on the path pattern. The response includes the partner identifier.

Example response from a partner-specific endpoint:
```json
{
  "message": "HELLO",
  "partner": "tymebank"
}
```

Authentication is required for all endpoints using the same API key.

## Cleanup

To remove all deployed resources:

```