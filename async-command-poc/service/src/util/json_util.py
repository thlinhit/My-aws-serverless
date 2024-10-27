import json
from decimal import Decimal
from types import SimpleNamespace
from typing import Any


def dumps(json_body: dict, **kwargs) -> str:
    def default_serializer(obj: Any) -> Any:
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    return json.dumps(json_body, default=default_serializer, **kwargs)


def loads(json_str: str, **kwargs) -> dict:
    return json.loads(
        json_str,
        object_hook=lambda d: SimpleNamespace(**d),
        parse_float=Decimal,
        **kwargs,
    )
