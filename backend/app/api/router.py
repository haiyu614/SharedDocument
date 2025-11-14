from fastapi import APIRouter

from .routes import auth, collab, documents, versions


api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(versions.router, prefix="/documents", tags=["versions"])
api_router.include_router(collab.router, prefix="/collab", tags=["collaboration"])

