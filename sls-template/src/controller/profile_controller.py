import json

from aws_lambda_powertools.event_handler.router import ALBRouter

router = ALBRouter()


@router.get("/create")
def test():
    body = {
        "message": "Go Serverless v4.0! Your function executed successfully!",
    }

    response = {"statusCode": 200, "body": json.dumps(body)}

    return response
