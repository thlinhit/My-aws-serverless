### ACloudGuru
```bash
aws configure --profile ACCGURUA
```

```bash
AWS_PROFILE=ACCGURUA sls deploy
```


### Each Service

#### Account A
```bash
AWS_PROFILE=acloudguru2 sls vpc:deploy --region eu-west-1
```

```bash
AWS_PROFILE=acloudguru2 sls vpc-tgw:deploy --region eu-west-1
```
