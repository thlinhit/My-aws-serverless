from pydantic import BaseModel, Field


class ItemKey(BaseModel):
    pk: str = Field(frozen=True)
    sk: str = Field(frozen=True)
