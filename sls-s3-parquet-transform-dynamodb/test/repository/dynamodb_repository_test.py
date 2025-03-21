import os

from src.dto.profile import Profile
from src.repository.model.key import Key
from src.repository.model.profile_item import ProfileItem
from src.util import datetime_util

os.environ["REGION"] = "us-east-1"

from src.repository import dynamodb_repository


def test_get_table():
    template_table = dynamodb_repository.get_table("template_table")

    dynamodb_repository.update_item(
        table_name="template_table",
        item=ProfileItem(
            pk="PROFILE#1243",
            sk="PROFILE#1243",
            username="username",
            address="address",
            email="tothemoon@moon.com",
            signup_timestamp=datetime_util.utc_iso_now()
        )
    )

    item = dynamodb_repository.get_item("template_table", Key(pk="PROFILE#1243", sk="PROFILE#1243"))
    print(item)


# pytest ./test/repository/dynamodb_repository_test.py::test_dto_to_model
def test_dto_to_model():
    profile: Profile = Profile(**{
        "username": "johndoe",
        "email": "johndoe@example.com",
        "address": "123 Moon Street",
        "profileId": "9999"
    })
    profile_item: ProfileItem = ProfileItem.from_dto(profile)

    dynamodb_repository.update_item(table_name="template_table", item=profile_item)
    print(profile_item.model_dump_json())
