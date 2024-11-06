# tests/test_uuid_util.generate_uuid_from_json.py
import uuid

from src.util import uuid_util


def test_generate_uuid_with_simple_json():
    # Given
    json_body = {"key": "value"}

    # When
    result_1 = uuid_util.generate_uuid_from_json(json_body)
    result_2 = uuid_util.generate_uuid_from_json(json_body)

    # Then
    assert isinstance(result_1, uuid.UUID)
    assert isinstance(result_2, uuid.UUID)
    assert result_1 == result_2


def test_generate_uuid_with_nested_json():
    # Given
    json_body = {"key": {"nested_key": "nested_value"}}

    # When
    result = uuid_util.generate_uuid_from_json(json_body)

    # Then
    assert isinstance(result, uuid.UUID)
    expected_uuid = uuid_util.generate_uuid_from_json(json_body)
    assert result == expected_uuid


def test_generate_uuid_with_sorted_keys():
    # Given
    json_body_1 = {"a": 1, "b": 2}
    json_body_2 = {"b": 2, "a": 1}

    # When
    result_1 = uuid_util.generate_uuid_from_json(json_body_1)
    result_2 = uuid_util.generate_uuid_from_json(json_body_2)

    # Then
    assert result_1 == result_2


def test_generate_uuid_with_empty_json():
    # Given
    json_body = {}

    # When
    result = uuid_util.generate_uuid_from_json(json_body)

    # Then
    assert isinstance(result, uuid.UUID)
    expected_uuid = uuid_util.generate_uuid_from_json(json_body)
    assert result == expected_uuid


def test_generate_uuid_with_complex_json():
    # Given
    json_body = {"list": [1, 2, {"key": "value"}], "int": 123, "str": "test"}

    # When
    result = uuid_util.generate_uuid_from_json(json_body)

    # Then
    assert isinstance(result, uuid.UUID)
    expected_uuid = uuid_util.generate_uuid_from_json(json_body)
    assert result == expected_uuid
