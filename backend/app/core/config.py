from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置，支持从环境变量或 .env 中读取。"""

    project_name: str = "Collaborative Document Service"
    secret_key: str = "CHANGE_ME"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    database_url: str = "mysql+mysqlconnector://user:password@localhost:3306/collab_doc"
    redis_url: str | None = "redis://localhost:6379/0"

    cors_allow_origins: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

