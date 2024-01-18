from enum import Enum


class DomainCode(Enum):
    # Technical Error - startsWith 0
    UNKNOWN = (
        "000",
        "Generic Error. errorMessage={}",
    )
    VALIDATION_ERROR = (
        "001",
        "Validation Error. errorMessage={}",
    )
    FIREHOSE_PUT_ERROR = (
        "002",
        "Encountered Error While Putting Records to FireHose",
    )
    SQS_SEND_ERROR = "003", "Failed at sending message to sqs, sqsName={}, message={}, error={}"

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
        return f"ACTIMIZE_{self.value}"
