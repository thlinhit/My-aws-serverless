from src.dto.profile import Profile
from src.repository.model.profile_item import ProfileItem
from src.util import datetime_util


def test_mapper():
    profile: ProfileItem = ProfileItem(
        pk="PROFILE#1243", sk="PROFILE#1243", username="username", address="address", email="tothemoon@moon.com",
        signup_timestamp=datetime_util.utc_iso_now()
    )

    print(profile)
    print(profile.model_dump_json(by_alias=True))
    print("_++")
    profile_dto: Profile = profile.to_dto()
    print(profile_dto.model_dump_json(by_alias=True))
    print("_++")
    print(ProfileItem.from_dto(profile=profile_dto).model_dump_json(by_alias=True))
