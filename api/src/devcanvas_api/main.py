"""FastAPI 애플리케이션 진입점."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from devcanvas_api.core import settings
from devcanvas_api.generations import router as generations_router
from devcanvas_api.health import router as health_router


def create_app() -> FastAPI:
    """FastAPI 애플리케이션을 생성한다."""
    app = FastAPI(title=settings.app_name, debug=settings.debug)
    # CORS — dev(Next 3000 → API 8000) 허용. 프로덕션은 origins 제한 필요(ADR-0014).
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    app.include_router(generations_router)
    return app


app = create_app()
