from typing import Optional

from aws_lambda_powertools.utilities.parser import Field

from src.dto.profile import Profile
from src.repository.model.Item import Item
from src.repository.model.update_behavior import UpdateBehavior
from src.util import mapper, datetime_util


class ProfileItem(Item):
    username: str = Field(alias="username")
    address: str = Field(alias="address")
    email: str = Field(alias="email")
    signup_timestamp: Optional[str] = Field(
        default_factory=lambda: datetime_util.utc_iso_now(),
        alias="signupAt",
        metadata={**UpdateBehavior.WRITE_IF_NOT_EXIST.to_dict()}
    )

    def to_dto(self) -> Profile:
        return mapper.map(
            self,
            Profile,
            extra_fields={"profile_id": self.sk.replace("PROFILE#", "")}
        )

    @staticmethod
    def from_dto(profile: Profile):
        return mapper.map(
            profile,
            ProfileItem,
            extra_fields={
                "pk": ProfileItem.build_pk(profile.profile_id),
                "sk": ProfileItem.build_sk(profile.profile_id),
            }
        )

    @staticmethod
    def build_pk(profile_id: str):
        return f"PROF#{profile_id}"

    @staticmethod
    def build_sk(profile_id: str):
        return f"PROF#{profile_id}"