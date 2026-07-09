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
    glm_api_base: str = "https://open.bigmodel.cn/api/paas/v4"
    glm_model: str = "glm-5.2"
    # 전송 계층 재시도 정책(ADR-0007). 관측 결과 편집 턴 실패가 전부 transient http
    # (429/timeout)였음 — 스키마 위반은 0. 따라서 스키마 재프롬프트가 아니라 지수 백오프.
    glm_timeout: float = 120.0  # 편집 턴(거대 프롬프트)이 60s 초과 → 상향
    glm_max_retries: int = 2  # 총 시도 = 1 + max_retries
    glm_retry_base_delay: float = 1.0  # 지수 백오프 기준(초): delay = base * 2**attempt
    # CORS 허용 origin 목록(dev 기본 전체 허용). 프로덕션은 환경변수로 제한(ADR-0014).
    cors_origins: list[str] = ["*"]


settings = Settings()
