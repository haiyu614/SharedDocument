from __future__ import annotations

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from ...deps import get_auth_service
from ...schemas import auth as auth_schema
from ...services.auth_service import AuthService


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


@router.post("/register", response_model=auth_schema.UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: auth_schema.UserCreate,
    service: AuthService = Depends(get_auth_service),
) -> auth_schema.UserRead:
    return await service.register_user(payload)


@router.post("/login", response_model=auth_schema.TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
) -> auth_schema.TokenResponse:
    return await service.authenticate(form_data.username, form_data.password)


@router.get("/me", response_model=auth_schema.UserRead)
async def read_profile(
    token: str = Depends(oauth2_scheme),
    service: AuthService = Depends(get_auth_service),
) -> auth_schema.UserRead:
    user = await service.get_current_user(token)
    return auth_schema.UserRead.model_validate(user, from_attributes=True)


@router.get("/users", response_model=list[auth_schema.UserRead])
async def list_users(
    service: AuthService = Depends(get_auth_service),
) -> list[auth_schema.UserRead]:
    return await service.list_users()

