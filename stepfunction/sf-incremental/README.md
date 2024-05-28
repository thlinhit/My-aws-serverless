
## How to deploy to aws profile

### ACloudGuru
```bash
aws configure --profile acloudguru2
```

```bash
AWS_PROFILE=acloudguru2 sls deploy
```

### Deploy product

```shell
AWS_PROFILE=acloudguru2 sls sqs:deploy
```

```shell
AWS_PROFILE=acloudguru2 sls sf:deploy
```

```shell
AWS_PROFILE=acloudguru2 sls lambda-fns:deploy
```