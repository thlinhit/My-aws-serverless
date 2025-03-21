from exception.domain_code import DomainCode

import re


def convert_pattern(pattern: str) -> str:
    def replacer(match: re.Match) -> str:
        key = match.group(1)
        return f"{key}={{{key}}}"

    return re.sub(r'{(\w+)}', replacer, pattern)


class DomainError(Exception):
    def __init__(self, domain_code: DomainCode, **values):
        self.domain_code = domain_code
        self.values = values
        self.message = "[{}] - {}".format(
            domain_code.external_code, domain_code.internal_msg.format(**values)
        )
        super().__init__(self.message)

    def get_value(self, key):
        return self.values.get(key, None)
