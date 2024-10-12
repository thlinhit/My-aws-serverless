import os

from src.dto.account import Account
from src.repository import dynamodb_repository
from src.repository.model.account_item import AccountItem
from src.repository.model.key import Key

table_name = os.environ["DYNAMODB_TABLE"]


def get_account(account_number: str) -> Account:
    key = Key(pk=f"ACC#{account_number}", sk=f"ACC#{account_number}")
    return AccountItem(**dynamodb_repository.get_item(table_name=table_name, key=key)).to_dto()


def upsert_account(account: Account) -> Account:
    return AccountItem(**dynamodb_repository.update_item(table_name, AccountItem.from_dto(account))).to_dto()
