import http
import json

from aws_lambda_powertools.event_handler import Response, content_types
from aws_lambda_powertools.event_handler.router import ALBRouter

from src.dto.profile import Profile
from src.log.logger import logger
from src.repository import profile_repository
from src.resolver.alb_resolver import app

router = ALBRouter()


@router.get("/<profile_id>")
def get_profile(profile_id: str):
    logger.debug(f"Getting profile info, profile_id{profile_id}")

    profile: Profile = profile_repository.get_profile(profile_id)

    return Response(
        status_code=http.HTTPStatus.OK,
        body=profile,
        content_type=content_types.APPLICATION_JSON,
    )


@router.post("/create")
def create_profile():
    body = router.current_event.body
    logger.debug(f"Create profile info, body={router.current_event.json_body}")

    profile: Profile = Profile(**router.current_event.json_body)

    return Response(
        status_code=http.HTTPStatus.OK,
        body=profile_repository.upsert_profile(profile),
        content_type=content_types.APPLICATION_JSON,
    )
