
## How to deploy to aws profile

### ACloudGuru
```bash
aws configure --profile tx-sandbox
aws configure set aws_session_token <>
```


### Deploy DynamoDB
```bash
AWS_PROFILE=tx-sandbox sls dynamodb:deploy
```

### Insert the example items
```bash
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

```bash
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
```bash
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


### Deploy AppSync
```bash
AWS_PROFILE=tx-sandbox sls appsync:deploy
```



---
### Main Resolver Kinds:
* PIPELINE: For complex operations that can chain multiple functions
* UNIT: For simple, direct operations with a single data source
* None (default in v2 is PIPELINE)

Note: To simulate a UNIT resolver, use a PIPELINE with only one function

#### **PIPELINE Resolvers**
- Can execute multiple functions in sequence (like a pipeline)
- Use cases:
  - Complex operations requiring multiple data sources
  - Operations needing data transformation between steps
  - When you need to combine data from multiple sources
  - When you need pre/post processing of data
  - Authentication/authorization checks before data access
- Example: A query that needs to:
  - First check user permissions
  - Then fetch data from DynamoDB
  - Then enrich it with data from another source
  - Finally transform the result

#### **UNIT Resolvers**
- Single operation with one data source
- Use cases:
  - Simple CRUD operations
  - Direct database queries
  - When you only need to interact with one data source
  - Simple transformations
- Example: A simple query to fetch an item from DynamoDB


You're using PIPELINE resolvers, which is the default in v2 of the plugin. Even though your operations are currently simple (one function each), using PIPELINE resolvers gives you the flexibility to add more functions later if needed.

Best Practices:
- Use UNIT when you're certain you'll only ever need one data source
- Use PIPELINE when:
  - You might need to add more functionality later
  - You need to perform multiple operations
  - You need to implement complex business logic
  - You need to combine data from multiple sources

In v2 of the serverless-appsync-plugin, PIPELINE is recommended even for simple operations, as it provides more flexibility for future extensions of your resolvers.
