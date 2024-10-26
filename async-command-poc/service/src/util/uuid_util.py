import hashlib
import uuid

from src.util import json_util

NAMESPACE_ORDER = uuid.UUID("12345678-1234-5678-1234-567812345678")


def generate_uuid_from_json(json_body: dict) -> uuid.UUID:
    json_str = json_util.dumps(json_body, sort_keys=True)

    hash_digest = hashlib.sha256(NAMESPACE_ORDER.bytes + json_str.encode()).digest()

    return uuid.UUID(bytes=hash_digest[:16])
