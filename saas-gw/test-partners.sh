#!/bin/bash

# Get partner API keys from SSM
get_partner_api_key() {
  local partner=$1
  local api_key=$(AWS_PROFILE=tx-sandbox aws ssm get-parameter --name "/saas/apikey/$partner" --with-decryption --query "Parameter.Value" --output text)
  echo "$api_key"
}

# Get the CloudFront domain name
CF_DOMAIN=$(AWS_PROFILE=tx-sandbox aws cloudformation describe-stacks --stack-name saas-gw-api-dev --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDomainName'].OutputValue" --output text)
if [ -z "$CF_DOMAIN" ]; then
  echo "CloudFront domain not found. Make sure the service is deployed correctly."
  exit 1
fi

echo "Testing partner endpoints via CloudFront distribution: $CF_DOMAIN"
echo

# Test different partner paths
partners=("tymebank" "sanlam" "abc")

for partner in "${partners[@]}"; do
  echo "Testing $partner endpoint..."
  
  # Skip newpartner for API key retrieval (not in SSM)
  if [ "$partner" == "newpartner" ]; then
    echo "Note: 'newpartner' is not configured - expecting auth failure"
    API_KEY="invalid-key"
  else
    # Get partner-specific API key from SSM
    API_KEY=$(get_partner_api_key "$partner")
    echo "Using API Key for $partner: ${API_KEY:0:5}...${API_KEY: -5}"
  fi
  
  # Make request to partner-specific endpoint
  response=$(curl -s -X POST "https://$CF_DOMAIN/api/$partner/hello" \
    -H "x-api-key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"test": "data"}')
  
  echo "Response: $response"
  echo
done

echo "Testing complete!" 