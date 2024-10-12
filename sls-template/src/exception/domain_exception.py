import json

from src.exception.domain_code import DomainCode

PREFIX_CAP_LOAN_ACCOUNT_ERROR = "124"


class DomainException(Exception):
    domain_code: DomainCode = None
    values = None

    def __init__(self, domain_code: DomainCode, *values):
        self.domain_code = domain_code
        self.message = "[{}] - {}".format(domain_code.external_code, domain_code.internal_msg.format(*values))
        super().__init__(self.message)

    def __str__(self):
        error = {
            "errors": [
                {
                    "errorCode": f"{self.domain_code.external_code}",
                    "errorMessage": f"{self.message}",
                }
            ]
        }
        return json.dumps(error)

    def get_extra_values(self, index):
        return self.values[index]
