"""FastAPI 애플리케이션 진입점."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from devcanvas_api.core import settings
from devcanvas_api.generations import router as generations_router
from devcanvas_api.health import router as health_router
from devcanvas_api.sessions import router as sessions_router


def create_app() -> FastAPI:
    """FastAPI 애플리케이션을 생성한다."""
    app = FastAPI(title=settings.app_name, debug=settings.debug)
    # CORS — origins 는 settings.cors_origins 에서 제어(ADR-0014). dev 기본 전체 허용.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    app.include_router(generations_router)
    app.include_router(sessions_router)
    return app


app = create_app()
