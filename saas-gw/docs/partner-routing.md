# Partner-Specific Routing Documentation

## Overview

This document explains how we've implemented partner-specific routing in our API Gateway and CloudFront distribution. This setup allows partners like Tymebank and Sanlam to access the API through distinct URLs while all requests are processed by the same Lambda function.

## Architecture

```
                                          ┌─────────────────────┐
                                          │                     │
                                          │   Lambda Function   │
┌────────────┐    ┌────────────────┐     │                     │
│  Partner   │    │                 │     │  Identifies partner │
│  Request   │───▶│    CloudFront   │────▶│  from path and      │
│            │    │                 │     │  processes request  │
└────────────┘    └────────────────┘     │                     │
                          │              └─────────────────────┘
                          │
                          ▼
                  ┌────────────────┐
                  │                 │
                  │   API Gateway   │
                  │                 │
                  └────────────────┘
```

## Implementation Details

### 1. API Gateway Configuration

We've configured API Gateway with multiple endpoints, all pointing to the same Lambda function:

```yaml
functions:
  hello:
    handler: src/handlers/hello.handler
    events:
      - http:
          path: api/abc/hello
          method: post
          private: true  # Requires API key
          cors: true
      - http:
          path: api/tymebank/hello
          method: post
          private: true
          cors: true
      - http:
          path: api/sanlam/hello
          method: post
          private: true
          cors: true
```

### 2. CloudFront Distribution

CloudFront is configured with path patterns to route partner-specific URLs to the API Gateway:

```yaml
CacheBehaviors:
  # Tymebank path pattern
  - PathPattern: "api/tymebank/*"
    TargetOriginId: ApiGatewayOrigin
    # ... additional configuration ...
  # Sanlam path pattern  
  - PathPattern: "api/sanlam/*"
    TargetOriginId: ApiGatewayOrigin
    # ... additional configuration ...
```

### 3. Lambda Function

The Lambda function is designed to identify which partner is making the request based on the path:

```python
# Determine which partner is calling (if any)
partner = "default"

# Check if this is a partner-specific path
tymebank_pattern = r'^/api/tymebank.*'
sanlam_pattern = r'^/api/sanlam.*'

if re.match(tymebank_pattern, path):
    partner = "tymebank"
elif re.match(sanlam_pattern, path):
    partner = "sanlam"

# Add partner information to the response
response = {
    # ... other fields ...
    "body": json.dumps({
        "message": "HELLO",
        "partner": partner
    })
}
```

## Partner URLs

The following URLs are available for partners:

1. **Tymebank**: `https://d2h0ogwl3eqsat.cloudfront.net/api/tymebank/hello`
2. **Sanlam**: `https://d2h0ogwl3eqsat.cloudfront.net/api/sanlam/hello`
3. **Default/Original**: `https://d2h0ogwl3eqsat.cloudfront.net/api/abc/hello`

## Authentication

All endpoints use the same API key authentication. The API key must be included in the `x-api-key` header for all requests:

```
x-api-key: 5bNlyEaIlq3qjtfaga3Pm67AiUv5ERV7CEnoyVfc
```

## Response Format

The Lambda function identifies the partner from the path and includes this information in the response:

```json
{
  "message": "HELLO",
  "partner": "tymebank"  // or "sanlam" or "default"
}
```

## Benefits of This Approach

1. **Simplified Management**: All partners use the same API implementation, reducing maintenance overhead
2. **Consistent Authentication**: The same API key is used for all partners, simplifying key management
3. **Partner Tracking**: Each partner is identified in the code, allowing for partner-specific logging and metrics
4. **Flexible Routing**: New partners can be added by configuring new path patterns and updating the Lambda function
5. **Performance**: CloudFront provides caching and edge location benefits for all partners

## Adding New Partners

To add a new partner:

1. **Update serverless.yml**:
   - Add a new HTTP event in the Lambda function section with the partner-specific path
   - Add a new cache behavior in the CloudFront configuration with the partner path pattern

2. **Update Lambda function**:
   - Add a new path pattern for the partner
   - Update the partner detection logic

3. **Deploy the changes**:
   ```
   npm run deploy
   ```

## Future Enhancements

1. **Partner-Specific API Keys**: Implement separate API keys for each partner
2. **Usage Plans**: Set up throttling and quota limits per partner
3. **Custom Domains**: Implement custom domain names for each partner
4. **Enhanced Logging**: Add partner-specific logging and monitoring
5. **Request Validation**: Implement partner-specific request validation 