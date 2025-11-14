from __future__ import annotations

from fastapi import APIRouter, Depends, status

from ...deps import get_auth_service, get_document_service
from ...schemas import document as document_schema
from ...services.auth_service import AuthService
from ...services.document_service import DocumentService
from .auth import oauth2_scheme


router = APIRouter()


@router.get("", response_model=list[document_schema.DocumentSummary])
async def list_documents(
    service: DocumentService = Depends(get_document_service),
) -> list[document_schema.DocumentSummary]:
    return await service.list_documents()


@router.post("", response_model=document_schema.DocumentRead, status_code=status.HTTP_201_CREATED)
async def create_document(
    payload: document_schema.DocumentCreate,
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
    document_service: DocumentService = Depends(get_document_service),
) -> document_schema.DocumentRead:
    user = await auth_service.get_current_user(token)
    return await document_service.create_document(payload, owner=user)


@router.get("/{document_id}", response_model=document_schema.DocumentRead)
async def get_document(
    document_id: int,
    document_service: DocumentService = Depends(get_document_service),
) -> document_schema.DocumentRead:
    return await document_service.get_document(document_id)


@router.put("/{document_id}", response_model=document_schema.DocumentRead)
async def update_document(
    document_id: int,
    payload: document_schema.DocumentUpdate,
    document_service: DocumentService = Depends(get_document_service),
) -> document_schema.DocumentRead:
    return await document_service.update_document(document_id, payload)

