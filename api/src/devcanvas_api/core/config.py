"""애플리케이션 설정."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """환경 변수 기반 설정."""

    model_config = SettingsConfigDict(
        env_prefix="DEVCANVAS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "DevCanvas API"
    debug: bool = False
    glm_api_key: str | None = None
    glm_api_base: str | None = None


settings = Settings()
