# Introduction
This guide provides step-by-step instructions for deploying and testing the Lending Service, which uses AWS DynamoDB for data storage and AWS AppSync for API functionality.

# Prerequisites
* AWS CLI installed and configured
* Serverless Framework installed (npm install -g serverless)
* Access to the TymeX AWS account and Get the credentials for tymex-sandbox

## AWS Configuration

```
aws configure --profile tx-sandbox
aws configure set aws_session_token <your-session-token> --profile tx-sandbox
```

# Deployment Steps

## Deploy DynamoDB

```bash
AWS_PROFILE=tx-sandbox sls dynamodb:deploy
```

## Deploy DynamoDB
```
AWS_PROFILE=tx-sandbox sls appsync:deploy
```


# Testing
Insert sample loan application records into DynamoDB for testing:

```
AWS_PROFILE=tx-sandbox aws dynamodb put-item \
--region us-east-1 \
--table-name lend-aggregation-table \
--item '{
  "pk": {"S": "CUS#12345678"},
  "sk": {"S": "LOAN_APP#21968152"},
  "gsi1_pk": {"S": "CUS#12345678"},
  "gsi1_sk": {"S": "LOAN_APP#1694102400"},
  "gsi2_pk": {"S": "CUS#12345678"},
  "gsi2_sk": {"S": "LOAN_APP#APPROVED#1694102400"},
  "customer_id": {"S": "12345678"},
  "application_id": {"S": "21968152"},
  "debtor_account_number": {"S": "GB29NWBK60161331926819"},
  "date_application_created": {"S": "2023-09-01T10:15:30Z"},
  "dateApplicationCreatedTimestamp": {"N": "1694102400"},
  "status": {"S": "APPROVED"},
  "requested_amount": {"N": "5000.35"},
  "accepted_amount": {"N": "4500.12"},
  "contract_date": {"S": "2023-09-15"},
  "gross_income": {"N": "36000.00"}
}'
```
```
AWS_PROFILE=tx-sandbox aws dynamodb put-item \
--region us-east-1 \
--table-name lend-aggregation-table \
--item '{
  "pk": {"S": "CUS#12345678"},
  "sk": {"S": "LOAN_APP#21213237"},
  "gsi1_pk": {"S": "CUS#12345678"},
  "gsi1_sk": {"S": "LOAN_APP#1694188800"},
  "gsi2_pk": {"S": "CUS#12345678"},
  "gsi2_sk": {"S": "LOAN_APP#DECLINED#1694188800"},
  "customer_id": {"S": "12345678"},
  "application_id": {"S": "21213237"},
  "debtor_account_number": {"S": "GB29NWBK60161331926820"},
  "date_application_created": {"S": "2023-09-02T14:20:45Z"},
  "dateApplicationCreatedTimestamp": {"N": "1694188800"},
  "status": {"S": "DECLINED"},
  "requested_amount": {"N": "10000.00"},
  "gross_income": {"N": "25000.00"},
  "decline_reasons": {"S": "[\"Insufficient income\", \"High existing debt\"]"}
}'
```

```
AWS_PROFILE=tx-sandbox aws dynamodb put-item \
--region us-east-1 \
--table-name lend-aggregation-table \
--item '{
  "pk": {"S": "CUS#12345678"},
  "sk": {"S": "LOAN_APP#15629615"},
  "gsi1_pk": {"S": "CUS#12345678"},
  "gsi1_sk": {"S": "LOAN_APP#1694275200"},
  "gsi2_pk": {"S": "CUS#12345678"},
  "gsi2_sk": {"S": "LOAN_APP#IOD_LETTER_SENT#1694275200"},
  "customer_id": {"S": "12345678"},
  "application_id": {"S": "15629615"},
  "debtor_account_number": {"S": "GB29NWBK60161331926820"},
  "date_application_created": {"S": "2023-09-03T09:45:15Z"},
  "dateApplicationCreatedTimestamp": {"N": "1694275200"},
  "status": {"S": "IOD_LETTER_SENT"},
  "requested_amount": {"N": "7500.00"},
  "gross_income": {"N": "45000.00"}
}'
```

After inserting the sample data, you can verify it by:
1. Using the AWS Console to view the items in DynamoDB
2. Testing queries through the AppSync console
3. Running the application's test suite (if available)

# Troubleshooting
* If deployment fails, check AWS credentials and permissions
* Verify that your serverless.yml configuration is valid
* If data insertion fails, ensure the DynamoDB table exists and has the correct schema
* For AppSync issues, check the CloudWatch logs for detailed error messages
For more information, consult the project's internal documentation or reach out to the DevOps team.
