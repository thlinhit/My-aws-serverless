
## How to deploy to aws profile

### ACloudGuru
```bash
aws configure --profile acloudguru
```

```bash
AWS_PROFILE=acloudguru sls deploy --stage=dev
```

### Deploy product

```bash
AWS_PROFILE=acloudguru sls s3:deploy &&
AWS_PROFILE=acloudguru sls dynamodb:deploy &&
AWS_PROFILE=acloudguru sls firehose:deploy &&
AWS_PROFILE=acloudguru sls capturer:deploy
```