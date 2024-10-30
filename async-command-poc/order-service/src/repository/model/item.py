from typing import Optional

from aws_lambda_powertools.utilities.parser import Field
from pydantic import ConfigDict

from src.repository.model.key import Key
from src.repository.model.update_behavior import UpdateBehavior
from src.util import datetime_util


class Item(Key):
    model_config = ConfigDict(populate_by_name=True)

    pk: str = Field(frozen=True)
    sk: str = Field(frozen=True)
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime_util.utc_iso_now(),
        alias="createdAt",
        json_schema_extra={**UpdateBehavior.WRITE_IF_NOT_EXIST.to_dict()},
    )
    updated_at: Optional[str] = Field(
        default_factory=lambda: datetime_util.utc_iso_now(), alias="updatedAt"
    )
    updated_by: Optional[str] = Field(alias="updatedBy", default="SYSTEM")

    def get_key(self) -> Key:
        return Key(**self.model_dump())
