from pydantic import BaseModel, Field


class Account(BaseModel):
    account_number: str = Field(alias="accountNumber")
    account_type: str = Field(alias="accountType")