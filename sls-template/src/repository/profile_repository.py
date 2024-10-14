import os

from aws_lambda_powertools.utilities.parser import parse

from src.dto.profile import Profile
from src.repository import dynamodb_repository
from src.repository.model.key import Key
from src.repository.model.profile_item import ProfileItem

table_name = os.environ["DYNAMODB_TABLE"]


def get_profile(profile_id: str) -> Profile:
    key = Key(pk=ProfileItem.build_pk(profile_id), sk=ProfileItem.build_pk(profile_id))
    return parse(model=ProfileItem, event=dynamodb_repository.get_item(table_name=table_name, key=key)).to_dto()


def upsert_profile(profile: Profile) -> Profile:
    return parse(model=ProfileItem, event=dynamodb_repository.update_item(table_name, ProfileItem.from_dto(profile))).to_dto()
