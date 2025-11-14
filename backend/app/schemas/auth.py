from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: Optional[datetime] = None


class RoleRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr | None = None


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)
    role_name: str | None = None


class UserRead(UserBase):
    id: int
    role: RoleRead | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}

