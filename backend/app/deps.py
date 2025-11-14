from __future__ import annotations

from collections.abc import AsyncGenerator, Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from .core.config import Settings, get_settings
from .db.session import get_db
from .services.auth_service import AuthService
from .services.collab_service import CollaborationService
from .services.document_service import DocumentService
from .services.version_service import VersionService


def get_settings_dep() -> Settings:
    return get_settings()


def get_db_session() -> Generator[Session, None, None]:
    yield from get_db()


async def get_auth_service(
    db: Session = Depends(get_db_session),
    settings: Settings = Depends(get_settings_dep),
) -> AsyncGenerator[AuthService, None]:
    service = AuthService(db=db, settings=settings)
    try:
        yield service
    finally:
        await service.dispose()


async def get_document_service(
    db: Session = Depends(get_db_session),
) -> AsyncGenerator[DocumentService, None]:
    service = DocumentService(db=db)
    try:
        yield service
    finally:
        await service.dispose()


async def get_version_service(
    db: Session = Depends(get_db_session),
) -> AsyncGenerator[VersionService, None]:
    service = VersionService(db=db)
    try:
        yield service
    finally:
        await service.dispose()


async def get_collaboration_service(
    settings: Settings = Depends(get_settings_dep),
) -> AsyncGenerator[CollaborationService, None]:
    service = CollaborationService(settings=settings)
    try:
        yield service
    finally:
        await service.dispose()

