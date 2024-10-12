from aws_lambda_powertools.utilities.parser import Field

from src.dto.account import Account
from src.repository.model.Item import Item
from src.util import mapper, datetime_util


class AccountItem(Item):
    account_number: str = Field(alias="accountNumber")
    account_type: str = Field(alias="accountType")

    def to_dto(self) -> Account:
        return mapper.map(
            self,
            Account,
        )

    @staticmethod
    def from_dto(account: Account):
        return mapper.map(
            account,
            AccountItem,
            extra_fields={
                "pk": f"ACC#{account.account_number}",
                "sk": f"PROF#{account.account_number}"
            }
        )
