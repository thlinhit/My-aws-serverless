import http
import os

from src.dto.profile import Profile

os.environ["REGION"] = "us-east-1"
os.environ["DYNAMODB_TABLE"] = "template_table"

from src.controller import profile_controller
from src.repository import dynamodb_repository
from src.repository.model.profile_item import ProfileItem
from src.util import datetime_util


def test_get_profile():
    # Given
    dynamodb_repository.update_item(
        table_name="template_table",
        item=ProfileItem(
            pk="PROFILE#1234",
            sk="PROFILE#1234",
            username="linhtruong",
            address="Ho Chi Minh city",
            email="tothemoon@moon.com",
            signup_timestamp=datetime_util.utc_iso_now()
        )
    )

    # When
    res = profile_controller.get_profile(profile_id="1234")

    # Then
    assert res.status_code is http.HTTPStatus.OK
    assert res.body is not None
    assert isinstance(res.body, Profile)
    profile = res.body
    assert profile.profile_id == "1234"
    assert profile.email == "tothemoon@moon.com"
    assert profile.address == "Ho Chi Minh city"
    assert profile.username == "linhtruong"
