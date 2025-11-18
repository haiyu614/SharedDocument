from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ..core.config import Settings
from ..core.security import create_access_token, get_password_hash, verify_password
from ..models import role as role_model
from ..models import user as user_model
from ..schemas import auth as auth_schema


class AuthService:
    """负责用户注册、登录、权限相关逻辑的服务层。"""

    def __init__(self, db: Session, settings: Settings):
        self._db = db
        self._settings = settings

    async def dispose(self) -> None:
        """供依赖释放资源时调用。"""
        # 当前服务未持有额外资源，保留以便后续扩展。
        return None

    async def register_user(self, payload: auth_schema.UserCreate) -> auth_schema.UserRead:
        """注册新用户，默认角色为 editor。"""
        existing = (
            self._db.query(user_model.User)
            .filter(user_model.User.username == payload.username)
            .one_or_none()
        )
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")

        role_name = payload.role_name or "editor"
        role = (
            self._db.query(role_model.Role)
            .filter(role_model.Role.name == role_name)
            .one_or_none()
        )
        if not role:
            role = role_model.Role(name=role_name, description=f"Auto created role {role_name}")
            self._db.add(role)
            self._db.flush()

        new_user = user_model.User(
            username=payload.username,
            email=payload.email,
            password_hash=get_password_hash(payload.password),
            role_id=role.id,
        )
        self._db.add(new_user)
        self._db.commit()
        self._db.refresh(new_user)
        return auth_schema.UserRead.model_validate(new_user, from_attributes=True)

    async def authenticate(self, username: str, password: str) -> auth_schema.TokenResponse:
        user = (
            self._db.query(user_model.User)
            .filter(user_model.User.username == username)
            .one_or_none()
        )
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

        expires = timedelta(minutes=self._settings.access_token_expire_minutes)
        token = create_access_token(subject=user.id, expires_delta=expires)
        expires_at = datetime.now(timezone.utc) + expires
        return auth_schema.TokenResponse(access_token=token, expires_at=expires_at)

    async def decode_token(self, token: str) -> user_model.User:
        try:
            payload = jwt.decode(token, self._settings.secret_key, algorithms=[self._settings.algorithm])
        except JWTError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token 无效") from exc
        user_id: Optional[str] = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token 缺少 sub")
        user = self._db.get(user_model.User, int(user_id))
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
        return user

    async def get_current_user(self, token: str) -> user_model.User:
        return await self.decode_token(token)

    async def list_users(self) -> List[auth_schema.UserRead]:
        users = self._db.query(user_model.User).all()
        return [auth_schema.UserRead.model_validate(item, from_attributes=True) for item in users]

