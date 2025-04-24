#!/bin/bash

# API Gateway endpoint and API key from serverless deploy output
API_ENDPOINT="https://7aagni4blc.execute-api.us-east-1.amazonaws.com/dev/api/sanlam/hello"
API_KEY="Ax7IFITSpb8ERQzmbJZQS3E1aeAY4WFL6kGTNhu7"

# Get CloudFront domain
# echo "Getting CloudFront distribution info..."
# CLOUDFRONT_ID=$(AWS_PROFILE=tx-sandbox aws cloudformation list-stack-resources --stack-name saas-gw-api-dev | grep -A 1 CloudFrontDistribution | grep PhysicalResourceId | awk -F'"' '{print $4}')
# echo "CloudFront ID: $CLOUDFRONT_ID"

# if [ -n "$CLOUDFRONT_ID" ]; then
#   CLOUDFRONT_DOMAIN=$(AWS_PROFILE=tx-sandbox aws cloudfront get-distribution --id $CLOUDFRONT_ID | grep DomainName | head -1 | awk -F'"' '{print $4}')
#   echo "CloudFront Domain: $CLOUDFRONT_DOMAIN"
  
#   # CloudFront endpoint
#   CLOUDFRONT_ENDPOINT="https://$CLOUDFRONT_DOMAIN/api/abc/hello"
  
#   # Test via CloudFront
#   echo -e "\nTesting via CloudFront:"
#   echo "Endpoint: $CLOUDFRONT_ENDPOINT"
#   curl -X POST "$CLOUDFRONT_ENDPOINT" \
#     -H "x-api-key: $API_KEY" \
#     -H "Content-Type: application/json" \
#     -v
# fi

# Test via API Gateway directly
echo -e "\nTesting via API Gateway directly:"
echo "Endpoint: $API_ENDPOINT"
curl -X POST "$API_ENDPOINT" \
  -H "x-api-key: $API_KEY" \
  # -H "Authorization: test-token" \
  -H "Content-Type: application/json" \
  -v 