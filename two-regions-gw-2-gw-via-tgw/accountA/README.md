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
AWS_PROFILE=ACCGURUA sls vpc:deploy
```

```bash
AWS_PROFILE=ACCGURUA sls vpc-ec2:deploy
```

```bash
AWS_PROFILE=ACCGURUA sls vpc-tgw:deploy
```
