# DynamoDB Design for Loan Application System

This document outlines the DynamoDB table design for storing loan application data. The design follows a single-table approach with composite keys and global secondary indexes (GSIs) to enable efficient querying patterns.

## Table Structure

The DynamoDB table is designed with the following key structure:

### Primary Index

| Attribute | Type | Description |
|-----------|------|-------------|
| pk (Partition Key) | String | Customer identifier prefixed with "CUS#" |
| sk (Sort Key) | String | Loan application identifier prefixed with "LOAN_APP#" |

### Global Secondary Index 1 (GSI1)

This index allows querying applications by creation date.

| Attribute | Type | Description |
|-----------|------|-------------|
| GSI1_PK (Partition Key) | String | Same as pk - "CUS#[customer_id]" |
| GSI1_SK (Sort Key) | String | "LOAN_APP#[dateApplicationCreatedTimestamp]" |

### Global Secondary Index 2 (GSI2)

This index allows querying applications by status and creation date.

| Attribute | Type | Description |
|-----------|------|-------------|
| GSI2_PK (Partition Key) | String | Same as pk - "CUS#[customer_id]" |
| GSI2_SK (Sort Key) | String | "LOAN_APP#[status]#[dateApplicationCreatedTimestamp]" |

## Item Attributes

Each item in the table represents a loan application and contains the following attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| pk | String | Partition key in format "CUS#[customer_id]" |
| sk | String | Sort key in format "LOAN_APP#[application_id]" |
| GSI1_PK | String | Same as pk |
| GSI1_SK | String | Format "LOAN_APP#[dateApplicationCreatedTimestamp]" |
| GSI2_PK | String | Same as pk |
| GSI2_SK | String | Format "LOAN_APP#[status]#[dateApplicationCreatedTimestamp]" |
| customer_id | String | Unique identifier for the customer |
| application_id | String | 8-digit numeric identifier for the loan application |
| debtor_account_number | String | Account number for the debtor (optional) |
| date_application_created | String | ISO 8601 formatted creation date (YYYY-MM-DDThh:mm:ssZ) |
| dateApplicationCreatedTimestamp | Number | Unix timestamp of creation date (used in GSIs) |
| status | String | Current status of the application (e.g., "APPROVED", "DECLINED", "IOD_LETTER_SENT") |
| requested_amount | Number | Amount requested by the customer (decimal with 2 decimal places) |
| accepted_amount | Number | Amount accepted by the lender (optional) |
| contract_date | String | Date of contract in YYYY-MM-DD format (optional) |
| gross_income | Number | Gross income of the applicant (optional) |
| decline_reasons | String | JSON array of decline reasons (only present for declined applications) |

## Example Items

### Approved Loan Application

```json
{
  "pk": "CUS#12345678",
  "sk": "LOAN_APP#21968152",
  "GSI1_PK": "CUS#12345678",
  "GSI1_SK": "LOAN_APP#1694102400",
  "GSI2_PK": "CUS#12345678",
  "GSI2_SK": "LOAN_APP#APPROVED#1694102400",
  "customer_id": "12345678",
  "application_id": "21968152",
  "debtor_account_number": "GB29NWBK60161331926819",
  "date_application_created": "2023-09-01T10:15:30Z",
  "dateApplicationCreatedTimestamp": 1694102400,
  "status": "APPROVED",
  "requested_amount": 5000.00,
  "accepted_amount": 4500.00,
  "contract_date": "2023-09-15",
  "gross_income": 36000.00
}
```

### Declined Loan Application

```json
{
  "pk": "CUS#12345678",
  "sk": "LOAN_APP#21213237",
  "GSI1_PK": "CUS#12345678",
  "GSI1_SK": "LOAN_APP#1694188800",
  "GSI2_PK": "CUS#12345678",
  "GSI2_SK": "LOAN_APP#DECLINED#1694188800",
  "customer_id": "12345678",
  "application_id": "21213237",
  "debtor_account_number": "GB29NWBK60161331926820",
  "date_application_created": "2023-09-02T14:20:45Z",
  "dateApplicationCreatedTimestamp": 1694188800,
  "status": "DECLINED",
  "requested_amount": 10000.00,
  "gross_income": 25000.00,
  "decline_reasons": "[\"Insufficient income\", \"High existing debt\"]"
}
```

### Loan Application with IOD Letter Sent

```json
{
  "pk": "CUS#12345678",
  "sk": "LOAN_APP#15629615",
  "GSI1_PK": "CUS#12345678",
  "GSI1_SK": "LOAN_APP#1694275200",
  "GSI2_PK": "CUS#12345678",
  "GSI2_SK": "LOAN_APP#IOD_LETTER_SENT#1694275200",
  "customer_id": "12345678",
  "application_id": "15629615",
  "debtor_account_number": "GB29NWBK60161331926820",
  "date_application_created": "2023-09-03T09:45:15Z",
  "dateApplicationCreatedTimestamp": 1694275200,
  "status": "IOD_LETTER_SENT",
  "requested_amount": 7500.00,
  "gross_income": 45000.00
}
```

## Access Patterns

The table design supports the following access patterns:

### 1. Get The number of all applications created within 12 months

This query uses GSI1 to retrieve the number of all applications created within 12 months for a specific customer, sorted by GSI1_SK (LOAN_APP#[dateApplicationCreatedTimestamp]).

```python
today = datetime.now()
twelve_months_ago = today - timedelta(days=365)
twelve_months_ago_iso = twelve_months_ago.strftime('%Y-%m-%dT%H:%M:%SZ')

partition_key_value = f"CUS#{customer_id}"

total_count = 0
last_evaluated_key = None

while True:
    query_params = {
        'IndexName': 'GSI1',
        'KeyConditionExpression': Key('gsi1_pk').eq(partition_key_value) & 
                                    Key('gsi1_sk').begins_with('LOAN_APP#'),
        'FilterExpression': Attr('gsi1_sk').gte('LOAN_APP#' + twelve_months_ago_iso),
        'ScanIndexForward': False,
        'Select': 'COUNT'
    }
    
    if last_evaluated_key:
        query_params['ExclusiveStartKey'] = last_evaluated_key
    
    response = table.query(**query_params)
    
    # Add to the total count
    total_count += response.get('Count', 0)
    
    # Check if we need to paginate
    last_evaluated_key = response.get('LastEvaluatedKey')
    if not last_evaluated_key:
        break

return total_count
```

### 2. Get the earliest loan application

This query uses GSI1 to retrieve the lastest loan application, sorted by GSI1_SK (LOAN_APP#[dateApplicationCreatedTimestamp]).

```python
# Create the partition key value for the customer
partition_key_value = f"CUS#{customer_id}"

# Query parameters
query_params = {
    'IndexName': 'GSI1',
    'KeyConditionExpression': Key('gsi1_pk').eq(partition_key_value) & 
                                Key('gsi1_sk').begins_with('LOAN_APP#'),
    'ScanIndexForward': False,  # Sort in descending order (newest first)
    'Limit': 1  # We only need the first item (latest application)
}

# Execute the query
response = table.query(**query_params)

# Get the items from the response
items = response.get('Items', [])

# Return the latest loan application or None if no applications found
return items[0] if items else None
```

### 3. Get the latest loan application with status "IOD_LETTER_SENT" for a customer

This query uses GSI2 to retrieve the latest application with a specific status for a customer.

```python
# Create the partition key value for the customer
partition_key_value = f"CUS#{customer_id}"

# Query parameters
query_params = {
    'IndexName': 'GSI2',
    'KeyConditionExpression': Key('gsi2_pk').eq(partition_key_value) & 
                                Key('gsi2_sk').begins_with('LOAN_APP#IOD_LETTER_SENT#'),
    'ScanIndexForward': False,  # Sort in descending order (newest first)
    'Limit': 1  # We only need the first item (latest application)
}

# Execute the query
response = table.query(**query_params)

# Get the items from the response
items = response.get('Items', [])

# Return the latest loan application or None if no applications found
return items[0] if items else None
```

## Additional Considerations

1. **Data Consistency**: When updating application status, ensure all GSI sort keys are updated accordingly to maintain query integrity.

2. **TTL Attribute**: If there's a requirement to automatically expire old applications, consider adding a TTL attribute.

3. **Key Size Limits**: DynamoDB has a 2KB limit for the combined size of partition and sort keys. The current design should stay well within this limit, but it's something to monitor if key patterns change.

4. **Projected Attributes**: Consider which attributes to project into each GSI based on the queries that will be run against them to minimize read capacity usage.