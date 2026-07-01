"""FastAPI 애플리케이션 진입점."""

from __future__ import annotations

from fastapi import FastAPI

from devcanvas_api.core import settings
from devcanvas_api.generations import router as generations_router
from devcanvas_api.health import router as health_router


def create_app() -> FastAPI:
    """FastAPI 애플리케이션을 생성한다."""
    app = FastAPI(title=settings.app_name, debug=settings.debug)
    app.include_router(health_router)
    app.include_router(generations_router)
    return app


app = create_app()
