from typing import Optional

from pydantic import ConfigDict
from aws_lambda_powertools.utilities.parser import Field

from src.repository.model.key import Key
from src.util import datetime_util


class Item(Key):
    model_config = ConfigDict(populate_by_name=True)

    pk: str = Field(frozen=True)
    sk: str = Field(frozen=True)
    created_at: Optional[str] = Field(default_factory=lambda: datetime_util.utc_iso_now(), alias="createdAt")
    updated_at: Optional[str] = Field(default_factory=lambda: datetime_util.utc_iso_now(), alias="updatedAt")
    updated_by: str = Field(alias="updatedBy", default="SYSTEM")

    def get_key(self) -> Key:
        return Key(**self.model_dump())
