from enum import Enum


class DomainCode(Enum):
    UNKNOWN = (
        "000",
        "Generic Error. errorMessage:{}",
    )
    VALIDATION_ERROR = (
        "001",
        "Validation Error. errorMessage:{}",
    )
    FIREHOSE_PUT_ERROR = (
        "002",
        "Encountered Error While Putting Records to FireHose",
    )
    SQS_SEND_ERROR = (
        "003",
        "Failed at sending message to sqs, sqsName:{}, message:{}, error:{}",
    )

    DYNAMODB_ERROR = (
        "004",
        "Failed integrate with DynamoDB, tableName:{}, message:{}, error:{}",
    )

    EXCEEDED_MAX_ATTEMPTS = ("005", "Exceeded max attempts")

    ITEM_NOT_FOUND = ("006", "Item not found")

    SQS_CHANGE_VISIBILITY_ERROR = (
        "007",
        "Couldn't change visibility, transactionKey:{}, queueUrl:{}, error:{}",
    )

    SQS_RETRY_NEXT_TIME = (
        "008",
        "The message will be retried in {} seconds, transactionKey:{}",
    )

    DYNAMODB_PUT_BATCH_ERROR = (
        "009",
        "The items can't put into DynamoDB, error:{}",
    )

    def __new__(cls, *values):
        instance = object.__new__(cls)
        instance._value_ = values[0]
        return instance

    def __init__(self, _: str, internal_msg: str = None):
        self._internal_msg_ = internal_msg

    def __str__(self):
        return self.value

    @property
    def internal_msg(self):
        return self._internal_msg_

    @property
    def code(self):
        return self._value_

    @property
    def external_code(self):
        return f"EXTERNAL_CODE {self.value}"
