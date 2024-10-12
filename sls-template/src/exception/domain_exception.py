from src.exception.domain_code import DomainCode


class DomainException(Exception):
    domain_code: DomainCode = None
    values = None

    def __init__(self, domain_code: DomainCode, *values):
        self.domain_code = domain_code
        self.internal_message = domain_code.internal_msg.format(*values)
        self.message = "[{}] - {}".format(
            domain_code.external_code, self.internal_message
        )
        super().__init__(self.message)

    def get_extra_values(self, index):
        return self.values[index]
