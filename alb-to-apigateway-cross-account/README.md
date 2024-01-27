
## How to deploy to aws profile

### ACloudGuru
```bash
aws configure --profile acloudguru2
```

```bash
AWS_PROFILE=acloudguru2 sls deploy
```


### Each Service

```bash
AWS_PROFILE=acloudguru2 sls private-alb:deploy
```

```bash
AWS_PROFILE=acloudguru2 sls test-alb-fn:deploy
```

```bash
AWS_PROFILE=acloudguru2 sls ingress-api-gateway:deploy
```



----
https://serverlessland.com/patterns/alb-lambda-rust