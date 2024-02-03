from boto3.dynamodb.types import TypeDeserializer


def convert_to_python_obj(dynamo_obj: dict) -> [dict, None]:
    if dynamo_obj is None:
        return dynamo_obj
    deserializer = TypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in dynamo_obj.items()}
