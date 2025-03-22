
## Local Development


### Lint codes
```shell
python3 -m black . && isort .
```

## Local Development Setup

1. Install dependencies
```shell
npm i &&  pip install --upgrade pip && pip install -r requirements.txt && pip install -r requirements-dev.txt
```
2. Start Docker Desktop & Spin up containers for local development
```shell
docker compose -p tc-lend-infra up -d 
```
3. Create dynamodb table
```shell
AWS_ACCESS_KEY_ID=dummy AWS_SECRET_ACCESS_KEY=dummy  aws dynamodb create-table \
   --table-name dummy_table \
   --attribute-definitions AttributeName=pk,AttributeType=S AttributeName=sk,AttributeType=S \
   --key-schema AttributeName=pk,KeyType=HASH AttributeName=sk,KeyType=RANGE \
   --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
   --endpoint-url http://localhost:8000 \
   --region eu-west-1
```

4. Run main method
[ENTRYPOINT](src/entrypoint/jobs/s3_to_dynamodb_glue_job.py)

5. Run test
```shell
pytest
```