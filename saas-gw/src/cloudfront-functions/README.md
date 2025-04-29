# CloudFront Function for Partner Path Rewriting

## Overview

This CloudFront Function implements a dynamic path rewriting mechanism that:

1. Extracts the partner ID from the URL path (`/api/{partnerId}/hello`)
2. Rewrites the URL to a common backend endpoint (`/api/hello`)
3. Preserves the original path and partner ID as custom headers

This approach simplifies backend development by having a single API endpoint handle requests for multiple partners.

## Implementation Details

### Path Pattern Matching

The function uses a regular expression to match paths in the format `/api/{partnerId}/hello`:

```javascript
var regex = /^\/api\/([^\/]+)\/hello(\/.*)?$/;
var match = uri.match(regex);
```

This extracts the partner ID from the path for further processing.

### Header Handling

Two custom headers are added to preserve information about the original request:

```javascript
// Add the original path as a header for reference
request.headers['x-original-path'] = {value: originalUri};

// Add the partner ID as a custom header
request.headers['x-partner-id'] = {value: partnerId};
```

These headers allow the backend Lambda function to know:
- Which partner the request was originally for
- What the original URL path was before rewriting

### Important Notes

1. **Header Case Sensitivity**: CloudFront Functions require all header names to be lowercase.
2. **Header Forwarding**: The CloudFront distribution must be configured to forward these custom headers to the origin.
3. **Lambda Integration**: The Lambda function should check for the `x-partner-id` and `x-original-path` headers to identify the partner.

## Usage

This function is automatically attached to the CloudFront distribution in the serverless.yml configuration for paths matching `api/*/hello*`, allowing it to handle any partner ID dynamically.

## Testing

You can test this implementation using the `test-partners.sh` script in the root directory, which will send requests to different partner endpoints and verify that the partner ID is correctly extracted and preserved. 