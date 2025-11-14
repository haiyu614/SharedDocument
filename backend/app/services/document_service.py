from __future__ import annotations

from typing import Iterable

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..models import document as document_model
from ..models import document_version as version_model
from ..models import edit_log as edit_log_model
from ..models import user as user_model
from ..schemas import document as document_schema
from ..schemas import version as version_schema


class DocumentService:
    """文档与版本的核心业务封装。"""

    def __init__(self, db: Session):
        self._db = db

    async def dispose(self) -> None:
        return None

    async def list_documents(self) -> list[document_schema.DocumentSummary]:
        stmt = (
            select(document_model.Document)
            .options(selectinload(document_model.Document.versions))
            .order_by(document_model.Document.updated_at.desc())
        )
        documents = self._db.scalars(stmt).all()
        return [
            document_schema.DocumentSummary(
                id=doc.id,
                title=doc.title,
                latest_version=(
                    version_schema.DocumentVersionRead.model_validate(doc.versions[-1], from_attributes=True)
                    if doc.versions
                    else None
                ),
            )
            for doc in documents
        ]

    async def create_document(
        self,
        payload: document_schema.DocumentCreate,
        owner: user_model.User,
    ) -> document_schema.DocumentRead:
        document = document_model.Document(title=payload.title, owner_id=owner.id)
        self._db.add(document)
        self._db.flush()

        initial_content = payload.initial_content or ""
        version = version_model.DocumentVersion(
            document_id=document.id,
            version_number=1,
            content=initial_content,
            created_by=owner.id,
        )
        self._db.add(version)
        self._db.flush()

        document.current_version_id = version.id
        self._db.commit()
        self._db.refresh(document)
        self._db.refresh(document, attribute_names=["versions"])
        return document_schema.DocumentRead.model_validate(document, from_attributes=True)

    async def get_document(self, document_id: int) -> document_schema.DocumentRead:
        stmt = (
            select(document_model.Document)
            .options(
                selectinload(document_model.Document.owner),
                selectinload(document_model.Document.versions),
            )
            .filter(document_model.Document.id == document_id)
        )
        document = self._db.scalars(stmt).one_or_none()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")
        return document_schema.DocumentRead.model_validate(document, from_attributes=True)

    async def update_document(
        self,
        document_id: int,
        payload: document_schema.DocumentUpdate,
    ) -> document_schema.DocumentRead:
        document = self._db.get(document_model.Document, document_id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")

        if payload.title is not None:
            document.title = payload.title
        if payload.is_archived is not None:
            document.is_archived = payload.is_archived

        self._db.commit()
        self._db.refresh(document)
        return document_schema.DocumentRead.model_validate(document, from_attributes=True)

