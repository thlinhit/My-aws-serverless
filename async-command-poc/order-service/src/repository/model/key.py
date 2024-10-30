from pydantic import BaseModel, Field


class Key(BaseModel):
    pk: str = Field(frozen=True)
    sk: str = Field(frozen=True)
