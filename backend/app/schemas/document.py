from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .auth import UserRead
from .version import DocumentVersionRead, DiffEntry


class DocumentBase(BaseModel):
    title: str = Field(min_length=1, max_length=150)


class DocumentCreate(DocumentBase):
    initial_content: str | None = None


class DocumentUpdate(DocumentBase):
    is_archived: Optional[bool] = None


class DocumentRead(DocumentBase):
    id: int
    owner: Optional[UserRead] = None
    current_version_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentSummary(DocumentBase):
    id: int
    latest_version: Optional[DocumentVersionRead] = None

    model_config = {"from_attributes": True}


class DocumentDiff(BaseModel):
    from_version: int
    to_version: int
    entries: list[DiffEntry]

