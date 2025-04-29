#!/bin/bash

# Script to create SSM parameters for partner API keys

# AWS profile to use
PROFILE="tx-sandbox"

# Partner API keys - same as in serverless.yml
TYMEBANK_API_KEY="tymebank-api-key-b821c98d8fe3"
SANLAM_API_KEY="sanlam-api-key-8a9d2710c54f"
ABC_API_KEY="abc-api-key-6e7f359a1d2b"

echo "Creating SSM parameters for partner API keys..."

# Create SSM parameters
# Using --overwrite to update if they already exist
AWS_PROFILE=$PROFILE aws ssm put-parameter \
  --name "/saas/apikey/tymebank" \
  --value "$TYMEBANK_API_KEY" \
  --type "SecureString" \
  --description "API key for Tymebank partner" \
  --overwrite

AWS_PROFILE=$PROFILE aws ssm put-parameter \
  --name "/saas/apikey/sanlam" \
  --value "$SANLAM_API_KEY" \
  --type "SecureString" \
  --description "API key for Sanlam partner" \
  --overwrite

AWS_PROFILE=$PROFILE aws ssm put-parameter \
  --name "/saas/apikey/abc" \
  --value "$ABC_API_KEY" \
  --type "SecureString" \
  --description "API key for ABC partner" \
  --overwrite

echo "SSM parameters created successfully." 