
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
AWS_PROFILE=acloudguru2 sls vpc:deploy
```

```bash
AWS_PROFILE=acloudguru2 sls private-alb:deploy
```

```bash
AWS_PROFILE=acloudguru2 sls test-private-alb-fn:deploy
```


```bash
AWS_PROFILE=acloudguru2 sls test-alb-fn:deploy
```

```bash
AWS_PROFILE=acloudguru2 sls ingress-rest-api-gateway:deploy
```



----
https://serverlessland.com/patterns/alb-lambda-rust ✅


https://github.com/aws-samples/aws-apigw-http-api-private--integrations/blob/main/templates/APIGW-HTTP-private-integration-ALB-ecs.yml


https://tmmr.uk/post/api-gateway/api-gateway-to-api-gateway-proxy/


https://priyank-agarwal.medium.com/expose-and-access-private-api-in-amazon-api-gateway-540c513eec60


https://medium.com/swlh/aws-api-gateway-private-integration-with-http-api-and-a-vpc-link-602360a1cd84


https://manurana.medium.com/tutorial-connecting-an-api-gateway-to-a-vpc-using-vpc-link-682a21281263


https://github.com/aws-samples/Implementing-custom-domain-names-for-Amazon-API-Gateway-private-endpoints