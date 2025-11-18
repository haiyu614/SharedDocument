from __future__ import annotations

from datetime import datetime
from typing import Optional, Union

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
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)
    role_name: Optional[str] = None


class UserRead(UserBase):
    id: int
    role: Optional[RoleRead] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

