import re
from typing import Type

from annotated_types import T
from pydantic import BaseModel


def map(
    source_model: BaseModel,
    target_model_class: Type[T],
    field_mapping: dict = None,
    extra_fields: dict = None,
) -> T:
    source_dict = source_model.model_dump(by_alias=True)
    source_dict = {k: v for k, v in source_dict.items() if v is not None}

    if field_mapping:
        for source_field, target_field in field_mapping.items():
            if source_field in source_dict:
                source_dict[target_field] = source_dict.pop(source_field)

    if extra_fields:
        for extra_field, extra_value in extra_fields.items():
            source_dict[extra_field] = extra_value

    source_dict = {to_camel_case(k): v for k, v in source_dict.items()}

    return target_model_class(**source_dict)


def to_camel_case(snake_str: str) -> str:
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


# Function to convert camelCase to snake_case
def to_snake_case(camel_str: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", camel_str).lower()
