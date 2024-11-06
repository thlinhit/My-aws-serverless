# tests/test_json_util.py
import pytest
import json
from decimal import Decimal
from types import SimpleNamespace

from src.util.json_util import dumps, loads


def test_dumps_with_decimal():
    # Given
    json_body = {"value": Decimal("10.5")}

    # When
    result = dumps(json_body)

    # Then
    assert result == json.dumps({"value": 10.5})


def test_dumps_with_non_serializable_object():
    # Given
    class NonSerializable:
        pass

    json_body = {"value": NonSerializable()}

    # When / Then
    with pytest.raises(TypeError):
        dumps(json_body)


def test_loads_with_decimal():
    # Given
    json_str = '{"value": 10.5}'

    # When
    result = loads(json_str)

    # Then
    assert isinstance(result, SimpleNamespace)
    assert isinstance(result.value, Decimal)
    assert result.value == Decimal("10.5")


def test_loads_with_nested_structure():
    # Given
    json_str = '{"item": {"price": 99.99, "quantity": 2}}'

    # When
    result = loads(json_str)

    # Then
    assert isinstance(result, SimpleNamespace)
    assert isinstance(result.item, SimpleNamespace)
    assert isinstance(result.item.price, Decimal)
    assert isinstance(result.item.quantity, int)
    assert result.item.price == Decimal("99.99")
    assert result.item.quantity == 2


def test_dumps_and_loads_consistency():
    # Given
    json_body = {"value": Decimal("123.45"), "nested": {"key": "test"}}

    # When
    serialized = dumps(json_body)
    deserialized = loads(serialized)

    # Then
    assert isinstance(deserialized, SimpleNamespace)
    assert isinstance(deserialized.value, Decimal)
    assert deserialized.value == Decimal("123.45")
    assert isinstance(deserialized.nested, SimpleNamespace)
    assert deserialized.nested.key == "test"
