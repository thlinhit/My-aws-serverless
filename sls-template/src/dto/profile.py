from typing import Optional

from pydantic import BaseModel, Field


class Profile(BaseModel):
    profile_id: str = Field(alias='profileId')
    username: str = Field(alias="username")
    address: str = Field(alias="address")
    email: str = Field(alias="email")
    created_at: Optional[str] = Field(None, alias="createdAt")
    updated_at: Optional[str] = Field(None, alias="updatedAt")