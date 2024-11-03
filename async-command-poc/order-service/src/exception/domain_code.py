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

    EXCEEDED_MAX_ATTEMPTS = ("002", "Exceeded max attempts")

    SQS_SEND_ERROR = (
        "003",
        "Failed at sending message to sqs, sqsName:{}, message:{}, error:{}",
    )

    SQS_CHANGE_VISIBILITY_ERROR = (
        "004",
        "Couldn't change visibility, transactionKey:{}, queueUrl:{}, error:{}",
    )

    SQS_RETRY_NEXT_TIME = (
        "005",
        "The message will be retried in {} seconds, transactionKey:{}",
    )

    DYNAMODB_ERROR = (
        "006",
        "Failed integrate with DynamoDB, tableName:{}, error:{}",
    )

    ITEM_NOT_FOUND = ("007", "Item not found, table:{}, pk:{}, sk:{}")

    DYNAMODB_PUT_BATCH_ERROR = (
        "008",
        "The items can't put into DynamoDB, error:{}",
    )

    DYNAMODB_CONDITIONAL_CHECK_FAILED_ERROR = (
        "009",
        "Failed conditional check in the dynamodb, tableName:{}",
    )

    INVALID_ORDER_STATUS = (
        "010",
        "Order status is invalid, orderId:{}, userId:{}, expected:{}, actual:{}",
    )

    ITEM_ALREADY_EXISTS = ("011", "Item already exists, pk:{}, sk:{}")

    ORDER_NOT_FOUND = ("012", "Order not found, orderId:{}")

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
        return f"<EXTERNAL_CODE>{self.value}"
