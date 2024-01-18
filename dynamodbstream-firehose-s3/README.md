
## How to deploy to aws profile

### ACloudGuru
```bash
aws configure --profile acloudguru
```

```bash
AWS_PROFILE=acloudguru sls deploy
```

### Deploy product

```bash
AWS_PROFILE=acloudguru sls products:deploy