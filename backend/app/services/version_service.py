from __future__ import annotations

from difflib import ndiff

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import document as document_model
from ..models import document_version as version_model
from ..schemas import document as document_schema
from ..schemas import version as version_schema


class VersionService:
    def __init__(self, db: Session):
        self._db = db

    async def dispose(self) -> None:
        return None

    async def list_versions(self, document_id: int) -> list[version_schema.DocumentVersionRead]:
        document = self._ensure_document(document_id)
        stmt = (
            select(version_model.DocumentVersion)
            .filter(version_model.DocumentVersion.document_id == document.id)
            .order_by(version_model.DocumentVersion.version_number.desc())
        )
        versions = self._db.scalars(stmt).all()
        return [
            version_schema.DocumentVersionRead.model_validate(item, from_attributes=True) for item in versions
        ]

    async def get_version(self, document_id: int, version_id: int) -> version_schema.DocumentVersionRead:
        version = self._db.get(version_model.DocumentVersion, version_id)
        if not version or version.document_id != document_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="版本不存在")
        return version_schema.DocumentVersionRead.model_validate(version, from_attributes=True)

    async def compare_versions(self, document_id: int, from_version: int, to_version: int) -> document_schema.DocumentDiff:
        source = self._get_version_by_number(document_id, from_version)
        target = self._get_version_by_number(document_id, to_version)
        diff_entries: list[version_schema.DiffEntry] = []
        for diff in ndiff(source.content.splitlines(), target.content.splitlines()):
            op = diff[:2]
            text = diff[2:]
            if op == "  ":
                diff_entries.append(version_schema.DiffEntry(operation="equal", text=text, position=diff_entries.__len__()))
            elif op == "+ ":
                diff_entries.append(version_schema.DiffEntry(operation="insert", text=text, position=diff_entries.__len__()))
            elif op == "- ":
                diff_entries.append(version_schema.DiffEntry(operation="delete", text=text, position=diff_entries.__len__()))

        return document_schema.DocumentDiff(from_version=from_version, to_version=to_version, entries=diff_entries)

    def _ensure_document(self, document_id: int) -> document_model.Document:
        document = self._db.get(document_model.Document, document_id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")
        return document

    def _get_version_by_number(self, document_id: int, version_number: int) -> version_model.DocumentVersion:
        stmt = (
            select(version_model.DocumentVersion)
            .filter(
                version_model.DocumentVersion.document_id == document_id,
                version_model.DocumentVersion.version_number == version_number,
            )
        )
        version = self._db.scalars(stmt).one_or_none()
        if not version:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"版本 {version_number} 不存在")
        return version

