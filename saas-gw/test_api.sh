#!/bin/bash

# Replace with your actual API key and CloudFront domain
API_KEY="Ax7IFITSpb8ERQzmbJZQS3E1aeAY4WFL6kGTNhu7"
CF_DOMAIN="dh0fzevkjwvsf.cloudfront.net"
API_GATEWAY_URL="https://7aagni4blc.execute-api.us-east-1.amazonaws.com/dev"

# Test endpoints with CloudFront WITHOUT API key
echo "Testing with CloudFront (NO API KEY)..."

echo "Testing ABC Partner Path:"
echo "Endpoint: https://$CF_DOMAIN/api/abc/hello"
curl -X POST "https://$CF_DOMAIN/api/abc/hello" \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
echo -e "\n"

echo "Testing Tymebank Partner Path:"
echo "Endpoint: https://$CF_DOMAIN/api/tymebank/hello"
curl -X POST "https://$CF_DOMAIN/api/tymebank/hello" \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
echo -e "\n"

echo "Testing Sanlam Partner Path:"
echo "Endpoint: https://$CF_DOMAIN/api/sanlam/hello"
curl -X POST "https://$CF_DOMAIN/api/sanlam/hello" \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
echo -e "\n"

# Test with direct API Gateway URL WITHOUT API key
echo "Testing with Direct API Gateway (NO API KEY)..."

echo "Testing ABC Partner Path:"
echo "Endpoint: $API_GATEWAY_URL/api/abc/hello"
curl -X POST "$API_GATEWAY_URL/api/abc/hello" \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
echo -e "\n"

echo "Testing Tymebank Partner Path:"
echo "Endpoint: $API_GATEWAY_URL/api/tymebank/hello"
curl -X POST "$API_GATEWAY_URL/api/tymebank/hello" \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
echo -e "\n"

echo "Testing Sanlam Partner Path:"
echo "Endpoint: $API_GATEWAY_URL/api/sanlam/hello"
curl -X POST "$API_GATEWAY_URL/api/sanlam/hello" \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
echo -e "\n" 