
## How to deploy to aws profile

### ACloudGuru
```bash
aws configure --profile acloudguru2
```

```bash
AWS_PROFILE=acloudguru2 sls deploy
```

### Deploy product

```bash
AWS_PROFILE=acloudguru2 sls s3:deploy &&
AWS_PROFILE=acloudguru2 sls sqs:deploy &&
AWS_PROFILE=acloudguru2 sls dynamodb:deploy &&
AWS_PROFILE=acloudguru2 sls firehose:deploy &&
AWS_PROFILE=acloudguru2 sls capturer:deploy &&
AWS_PROFILE=acloudguru2 sls utility-fns:deploy
```