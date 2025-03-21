from application.etl.tranformation.base_transformer import DataTransformer
from application.etl.tranformation.loan_application_transformer import LoanApplicationTransformer
from exception.domain_code import DomainCode
from exception.domain_error import DomainError


class DataTransformerFactory:

    _transformers = {
        "LOAN_APPLICATION": LoanApplicationTransformer
    }

    @classmethod
    def create(cls, data_type: str) -> DataTransformer:
        if data_type not in cls._transformers:
            raise DomainError(DomainCode.NO_DATA_TRANSFORMER_FOUND, data_type=data_type)
        return cls._transformers[data_type]()
