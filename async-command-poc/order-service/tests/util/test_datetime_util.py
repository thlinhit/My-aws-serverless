# tests/test_time_utils.py
import pytest
import time
from datetime import datetime, timezone

from src.util.datetime_util import timestamp, utc_iso_now


def test_timestamp_is_current():
    # Given
    before = int(round(time.time() * 1000))

    # When
    result = timestamp()

    # Then
    after = int(round(time.time() * 1000))
    assert before <= result <= after, "Timestamp should be within the current time range."


def test_utc_iso_now_format():
    # When
    result = utc_iso_now()

    # Then
    # Ensure result ends with 'Z' and matches the expected ISO format
    assert result.endswith("Z"), "ISO format should end with 'Z'."
    try:
        # Attempt to parse the result back to a datetime object
        parsed_time = datetime.fromisoformat(result.replace("Z", "+00:00"))
        assert parsed_time.tzinfo == timezone.utc, "Parsed time should have UTC timezone."
    except ValueError:
        pytest.fail("utc_iso_now did not return a valid ISO formatted string.")


def test_utc_iso_now_is_current():
    # Given
    before = datetime.now(tz=timezone.utc).replace(microsecond=0)

    # When
    result = utc_iso_now()

    # Then
    after = datetime.now(tz=timezone.utc).replace(microsecond=0)
    parsed_time = datetime.fromisoformat(result)
    assert before <= parsed_time <= after, "utc_iso_now should return the current time in ISO format."
