pipx install poetry
## Local Development


Add new dependency for local development
```shell
poetry add pytest-env --group dev
```
Install dependencies
```shell
npm i && poetry install
```

```shell
poetry run pytest
```

```shell
AWS_PROFILE=tx-sandbox sls package
```
``
### Lint codes
```shell
python3 -m black . && isort .
```

2. Start Docker Desktop & Spin up containers for local development
```shell
docker compose -p poc-infra up -d 
```
3. Create dynamodb table
```shell
AWS_ACCESS_KEY_ID=dummy AWS_SECRET_ACCESS_KEY=dummy  aws dynamodb create-table \
   --table-name arb-poc-order-table \
   --attribute-definitions AttributeName=pk,AttributeType=S AttributeName=sk,AttributeType=S \
   --key-schema AttributeName=pk,KeyType=HASH AttributeName=sk,KeyType=RANGE \
   --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
   --endpoint-url http://localhost:8000
```

```shell
curl -X POST http://localhost:3000/ecommerce/orders \
     -H "Content-Type: application/json" \
     -d '{
            "userId": "user456",
            "products": [
                {
                    "id": "product1",
                    "name": "Product 1",
                    "price": 19.99,
                    "quantity": 2
                },
                {
                    "id": "product2",
                    "name": "Product 2",
                    "price": 5.99
                }
            ],
            "deliveryPrice": 5,
            "address": {
                "name": "John Doe",
                "streetAddress": "123 Main St",
                "city": "Anytown",
                "country": "USA",
                "phoneNumber": "123-456-7890"
            }
        }'
```


NOTE: retry using tenacity

### Lint codes
```shell
python3 -m black . && isort .
```

```bash
AWS_PROFILE=tx-sandbox sls package
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
   --table-name arb-poc-order-table \
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
    "id": "order123",
    "userId": "user456",
    "status": "PENDING",
    "products": [
        {
            "id": "product1",
            "name": "Product 1",
            "price": "19.99",
            "quantity": 2
        },
        {
            "id": "product2",
            "name": "Product 2",
            "price": "5.99"
        }
    ],
    "deliveryPrice": 5,
    "address": {
        "name": "John Doe",
        "streetAddress": "123 Main St",
        "city": "Anytown",
        "country": "USA",
        "phoneNumber": "123-456-7890"
    }
}'
```


```shell
curl -X GET http://localhost:3003/dev/template/profiles/9999
```

<!--
title: 'AWS Simple HTTP Endpoint example in Python'
description: 'This template demonstrates how to make a simple HTTP API with Python running on AWS Lambda and API Gateway using the Serverless Framework.'
layout: Doc
framework: v3
platform: AWS
language: python
authorLink: 'https://github.com/serverless'
authorName: 'Serverless, inc.'
authorAvatar: 'https://avatars1.githubusercontent.com/u/13742415?s=200&v=4'
-->

# Serverless Framework Python HTTP API on AWS

This template demonstrates how to make a simple HTTP API with Python running on AWS Lambda and API Gateway using the Serverless Framework.

This template does not include any kind of persistence (database). For more advanced examples, check out the [serverless/examples repository](https://github.com/serverless/examples/)  which includes DynamoDB, Mongo, Fauna and other examples.

## Usage

### Deployment

```
$ serverless deploy
```

After deploying, you should see output similar to:

```bash
Deploying aws-python-http-api-project to stage dev (us-east-1)

✔ Service deployed to stack aws-python-http-api-project-dev (140s)

endpoint: GET - https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/
functions:
  hello: aws-python-http-api-project-dev-hello (2.3 kB)
```

_Note_: In current form, after deployment, your API is public and can be invoked by anyone. For production deployments, you might want to configure an authorizer. For details on how to do that, refer to [http event docs](https://www.serverless.com/framework/docs/providers/aws/events/apigateway/).

### Invocation

After successful deployment, you can call the created application via HTTP:

```bash
curl https://xxxxxxx.execute-api.us-east-1.amazonaws.com/
```

Which should result in response similar to the following (removed `input` content for brevity):

```json
{
  "message": "Go Serverless v3.0! Your function executed successfully!",
  "input": {
    ...
  }
}
```

### Local development

You can invoke your function locally by using the following command:

```bash
serverless invoke local --function hello
```

Which should result in response similar to the following:

```
{
  "statusCode": 200,
  "body": "{\n  \"message\": \"Go Serverless v3.0! Your function executed successfully!\",\n  \"input\": \"\"\n}"
}
```

Alternatively, it is also possible to emulate API Gateway and Lambda locally by using `serverless-offline` plugin. In order to do that, execute the following command:

```bash
serverless plugin install -n serverless-offline
```

It will add the `serverless-offline` plugin to `devDependencies` in `package.json` file as well as will add it to `plugins` in `serverless.yml`.

After installation, you can start local emulation with:

```
serverless offline
```

To learn more about the capabilities of `serverless-offline`, please refer to its [GitHub repository](https://github.com/dherault/serverless-offline).

### Bundling dependencies

In case you would like to include 3rd party dependencies, you will need to use a plugin called `serverless-python-requirements`. You can set it up by running the following command:

```bash
serverless plugin install -n serverless-python-requirements
```

Running the above will automatically add `serverless-python-requirements` to `plugins` section in your `serverless.yml` file and add it as a `devDependency` to `package.json` file. The `package.json` file will be automatically created if it doesn't exist beforehand. Now you will be able to add your dependencies to `requirements.txt` file (`Pipfile` and `pyproject.toml` is also supported but requires additional configuration) and they will be automatically injected to Lambda package during build process. For more details about the plugin's configuration, please refer to [official documentation](https://github.com/UnitedIncome/serverless-python-requirements).
