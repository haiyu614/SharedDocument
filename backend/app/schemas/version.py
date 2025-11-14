from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel

from .auth import UserRead


class DocumentVersionBase(BaseModel):
    content: str


class DocumentVersionRead(BaseModel):
    id: int
    version_number: int
    created_at: datetime
    author: Optional[UserRead] = None

    model_config = {"from_attributes": True}


class DiffEntry(BaseModel):
    operation: Literal["insert", "delete", "equal"]
    text: str
    position: int

