from src.shared.exception.domain_code import DomainCode


class DomainError(Exception):
    def __init__(self, domain_code: DomainCode, *values):
        self.domain_code = domain_code
        self.message = "[{}] - {}".format(domain_code.external_code, domain_code.internal_msg.format(*values))
        super().__init__(self.message)
