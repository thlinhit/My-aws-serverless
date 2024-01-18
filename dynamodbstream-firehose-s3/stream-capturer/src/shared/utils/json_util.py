import decimal
import json
from typing import Any, Union


def default(obj):
    if isinstance(obj, decimal.Decimal):
        return str(obj)
    raise TypeError


def dumps(_obj: Any) -> str:
    return json.dumps(_obj, default=default)


def dumps_to_bytes(_obj: Any) -> bytes:
    return json.dumps(_obj, default=default).encode("utf-8")


def dumps_and_appends_new_line(_obj: Any) -> str:
    return json.dumps(_obj, default=default, separators=(",", ":")) + "\n"


def loads(__obj: Union[bytes, bytearray, memoryview, str]) -> Any:
    return json.loads(__obj)
