from src.repository.model.profile_item import ProfileItem
from src.util import datetime_util


def test_model():
    profile: ProfileItem = ProfileItem(
        pk="PROFILE#1243", sk="PROFILE#1243", username="username", address="address", email="email",
        signup_timestamp=datetime_util.utc_iso_now()
    )
    print(profile.get_key().model_dump_json())
    print(profile.model_dump_json())



