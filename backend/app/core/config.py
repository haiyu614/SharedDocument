from __future__ import annotations

from functools import lru_cache
from typing import Optional, List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置，支持从环境变量或 .env 中读取。"""

    project_name: str = "Collaborative Document Service"
    secret_key: str = "CHANGE_ME"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    database_url: str = "mysql+pymysql://root:123456@8.138.190.109:3306/shared_documents"
    redis_url: Optional[str] = None

    cors_allow_origins: List[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

