
## Local Development


### Lint codes
```shell
python3 -m black . && isort .
```

## Local Development Setup

1. Install dependencies
```shell
npm i &&  pip install --upgrade pip && pip install -r requirements-dev.txt
```
2. Start Docker Desktop & Spin up containers for local development
```shell
docker compose -p tc-lend-infra up -d 
```
3. Create dynamodb table
```shell
AWS_ACCESS_KEY_ID=dummy AWS_SECRET_ACCESS_KEY=dummy  aws dynamodb create-table \
   --table-name template_table \
   --attribute-definitions AttributeName=pk,AttributeType=S AttributeName=sk,AttributeType=S \
   --key-schema AttributeName=pk,KeyType=HASH AttributeName=sk,KeyType=RANGE \
   --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
   --endpoint-url http://localhost:8000
```

4. Run sls in local mode
```shell
serverless offline
```

## Available endpoint
```shell
curl -X POST http://localhost:3003/dev/template/profiles/create \
     -H "Content-Type: application/json" \
     -d '{
          "username": "johndoe",
          "email": "johndoe@example.com",
          "address": "123 Moon Street",
          "profileId": "9999"
         }'
```


```shell
curl -X GET http://localhost:3003/dev/template/profiles/9999
```