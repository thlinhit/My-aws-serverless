
## How to deploy to aws profile

### ACloudGuru
```bash
aws configure --profile tx-sandbox
aws configure set aws_session_token <>
```

```bash
AWS_PROFILE=tx-sandbox sls deploy
```

### Deploy product

```bash
AWS_PROFILE=tx-sandbox sls s3:deploy &&
AWS_PROFILE=tx-sandbox sls sqs:deploy &&
AWS_PROFILE=tx-sandbox sls dynamodb:deploy &&
AWS_PROFILE=tx-sandbox sls firehose:deploy &&
AWS_PROFILE=tx-sandbox sls capturer:deploy &&
AWS_PROFILE=tx-sandbox sls utility-fns:deploy
```