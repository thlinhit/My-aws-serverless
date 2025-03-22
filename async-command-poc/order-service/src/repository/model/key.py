from pydantic import Field

from src.domain.base import Base


class ItemKey(Base):
    pk: str = Field(frozen=True)
    sk: str = Field(frozen=True)
