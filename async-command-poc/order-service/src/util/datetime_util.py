import time
from datetime import datetime, timezone


def timestamp():
    return int(round(time.time() * 1000))


def utc_iso_now() -> str:
    return (
        datetime.now(tz=timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
