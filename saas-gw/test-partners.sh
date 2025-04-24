#!/bin/bash

# API Gateway endpoint and API key from serverless deploy output
API_KEY="Ax7IFITSpb8ERQzmbJZQS3E1aeAY4WFL6kGTNhu7"

# Get CloudFront domain
echo "Getting CloudFront distribution info..."
CLOUDFRONT_ID=$(AWS_PROFILE=tx-sandbox aws cloudformation list-stack-resources --stack-name saas-gw-api-dev | grep -A 1 CloudFrontDistribution | grep PhysicalResourceId | awk -F'"' '{print $4}')
echo "CloudFront ID: $CLOUDFRONT_ID"

if [ -n "$CLOUDFRONT_ID" ]; then
  CLOUDFRONT_DOMAIN=$(AWS_PROFILE=tx-sandbox aws cloudfront get-distribution --id $CLOUDFRONT_ID | grep DomainName | head -1 | awk -F'"' '{print $4}')
  echo "CloudFront Domain: $CLOUDFRONT_DOMAIN"
  
  # Test for Tymebank
  echo -e "\nTesting Tymebank Partner Path:"
  TYMEBANK_ENDPOINT="https://$CLOUDFRONT_DOMAIN/api/tymebank/hello"
  echo "Endpoint: $TYMEBANK_ENDPOINT"
  curl -X POST "$TYMEBANK_ENDPOINT" \
    -H "x-api-key: $API_KEY" \
    -H "Content-Type: application/json"
  
  # Test for Sanlam
  echo -e "\nTesting Sanlam Partner Path:"
  SANLAM_ENDPOINT="https://$CLOUDFRONT_DOMAIN/api/sanlam/hello"
  echo "Endpoint: $SANLAM_ENDPOINT"
  curl -X POST "$SANLAM_ENDPOINT" \
    -H "x-api-key: $API_KEY" \
    -H "Content-Type: application/json"
  
  # Test original path
  echo -e "\nTesting Original Path:"
  ORIGINAL_ENDPOINT="https://$CLOUDFRONT_DOMAIN/api/abc/hello"
  echo "Endpoint: $ORIGINAL_ENDPOINT"
  curl -X POST "$ORIGINAL_ENDPOINT" \
    -H "x-api-key: $API_KEY" \
    -H "Content-Type: application/json"
fi 