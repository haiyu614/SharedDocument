from __future__ import annotations

from fastapi import APIRouter, Depends

from ...deps import get_version_service
from ...schemas import document as document_schema
from ...schemas import version as version_schema
from ...services.version_service import VersionService


router = APIRouter()


@router.get("/{document_id}/versions", response_model=list[version_schema.DocumentVersionRead])
async def list_versions(
    document_id: int,
    service: VersionService = Depends(get_version_service),
) -> list[version_schema.DocumentVersionRead]:
    return await service.list_versions(document_id)


@router.get("/{document_id}/versions/{version_id}", response_model=version_schema.DocumentVersionRead)
async def get_version(
    document_id: int,
    version_id: int,
    service: VersionService = Depends(get_version_service),
) -> version_schema.DocumentVersionRead:
    return await service.get_version(document_id, version_id)


@router.get("/{document_id}/compare", response_model=document_schema.DocumentDiff)
async def compare_versions(
    document_id: int,
    from_version: int,
    to_version: int,
    service: VersionService = Depends(get_version_service),
) -> document_schema.DocumentDiff:
    return await service.compare_versions(document_id, from_version, to_version)

