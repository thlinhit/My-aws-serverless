
#### Account X
```bash
aws configure --profile ACCGURU2
```

```bash
AWS_PROFILE=ACCGURU2 sls deploy
```

```bash
AWS_PROFILE=ACCGURU2 sls vpc-x:deploy
```

```bash
AWS_PROFILE=ACCGURU2 sls vpc-x-ec2:deploy
```

# TODO: Change VPC subnets ip addresses + API Gateway URL serverless-compose.yml
```bash
AWS_PROFILE=ACCGURU2 sls vpc-x-ingress-rest-gw:deploy
```
```bash
AWS_PROFILE=ACCGURU2 sls transit-gateway:deploy
```



