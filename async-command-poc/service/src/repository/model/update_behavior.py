from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

UPDATE_BEHAVIOR_KEY = "UPDATE_BEHAVIOR"


class UpdateBehaviorValue(Enum):
    WRITE_IF_NOT_EXIST = "WRITE_IF_NOT_EXIST"


class UpdateBehaviorModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    value: UpdateBehaviorValue = Field(frozen=True, alias=UPDATE_BEHAVIOR_KEY)

    def to_dict(self):
        return self.model_dump(by_alias=True)


@dataclass(frozen=True)
class UpdateBehavior:
    KEY = UPDATE_BEHAVIOR_KEY
    WRITE_IF_NOT_EXIST = UpdateBehaviorModel(
        value=UpdateBehaviorValue.WRITE_IF_NOT_EXIST
    )
