
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
curl -X GET http://localhost:3003/dev/template/profiles/1234
```


## Usage

### Deployment

```
serverless deploy
```

After deploying, you should see output similar to:

```
Deploying "aws-python-http-api" to stage "dev" (us-east-1)

✔ Service deployed to stack aws-python-http-api-dev (85s)

endpoint: GET - https://6ewcye3q4d.execute-api.us-east-1.amazonaws.com/
functions:
  hello: aws-python-http-api-dev-hello (2.3 kB)
```

_Note_: In current form, after deployment, your API is public and can be invoked by anyone. For production deployments, you might want to configure an authorizer. For details on how to do that, refer to [http event docs](https://www.serverless.com/framework/docs/providers/aws/events/apigateway/).

### Invocation

After successful deployment, you can call the created application via HTTP:

```
curl https://xxxxxxx.execute-api.us-east-1.amazonaws.com/
```

Which should result in response similar to the following (removed `input` content for brevity):

```json
{
  "message": "Go Serverless v4.0! Your function executed successfully!"
}
```

### Local development

You can invoke your function locally by using the following command:

```
serverless invoke local --function hello
```

Which should result in response similar to the following:

```json
{
  "statusCode": 200,
  "body": "{\n  \"message\": \"Go Serverless v4.0! Your function executed successfully!\"}"
}
```

Alternatively, it is also possible to emulate API Gateway and Lambda locally by using `serverless-offline` plugin. In order to do that, execute the following command:

```
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

```
serverless plugin install -n serverless-python-requirements
```

Running the above will automatically add `serverless-python-requirements` to `plugins` section in your `serverless.yml` file and add it as a `devDependency` to `package.json` file. The `package.json` file will be automatically created if it doesn't exist beforehand. Now you will be able to add your dependencies to `requirements.txt` file (`Pipfile` and `pyproject.toml` is also supported but requires additional configuration) and they will be automatically injected to Lambda package during build process. For more details about the plugin's configuration, please refer to [official documentation](https://github.com/UnitedIncome/serverless-python-requirements).
