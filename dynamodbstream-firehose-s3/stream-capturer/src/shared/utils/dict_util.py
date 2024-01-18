from typing import Any


def key_exists(dict: Any, key_names: list[str]) -> bool:
    nested_dict = dict
    for key_name in key_names:
        try:
            if key_name in nested_dict:
                nested_dict = nested_dict[key_name]
            else:
                return False
        except Exception:
            return False
    return True
