# API Gateway with Lambda Backend

This project provisions an AWS API Gateway with a Lambda function backend using Serverless Framework v3.

## Features

- API Gateway endpoint at `api/abc/hello` (POST method)
- API key authentication required
- Python 3.12 Lambda function backend
- Returns a simple "HELLO" response

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

## Authentication

After deployment, you can find your API key in the AWS Console under API Gateway > API Keys, or by running:

```bash
aws apigateway get-api-keys --name-query "saas-gw-api-dev-apikey" --include-values
```

## Usage

To test the API, use curl or any API client with your API key:

```bash
curl -X POST https://your-api-id.execute-api.us-east-1.amazonaws.com/dev/api/abc/hello \
  -H "x-api-key: your-api-key" \
  -H "Content-Type: application/json"
```

The response should be:

```json
{
  "message": "HELLO"
}
```

## Cleanup

To remove all deployed resources:

```bash
npm run remove
``` 