from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, FastAPI
from fastapi.staticfiles import StaticFiles

from app.approvals.router import router as approvals_router
from app.auth.router import router as auth_router
from app.auth.service import build_auth_service
from app.config.router import router as config_router
from app.core.logging import configure_logging
from app.core.settings import get_settings
from app.integrations.router import router as integrations_router
from app.notifications.router import router as notifications_router
from app.projects.router import router as projects_router
from app.runs.router import router as runs_router
from app.web.router import build_browser_auth_service
from app.web.router import router as web_router

BASE_DIR = Path(__file__).resolve().parent


def _include_api_v1_routes(app: FastAPI, api_version: str) -> None:
    api_v1_router = APIRouter(prefix=f"/api/{api_version}")

    api_v1_router.include_router(auth_router)
    api_v1_router.include_router(projects_router)
    api_v1_router.include_router(integrations_router)
    api_v1_router.include_router(config_router)
    api_v1_router.include_router(runs_router)
    api_v1_router.include_router(approvals_router)
    api_v1_router.include_router(notifications_router)

    @api_v1_router.get("/health", include_in_schema=False)
    async def api_health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(api_v1_router)


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        docs_url=f"/api/{settings.api_version}/docs",
        openapi_url=f"/api/{settings.api_version}/openapi.json",
        redoc_url=None,
    )

    static_dir = BASE_DIR / "web" / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    app.include_router(web_router)
    _include_api_v1_routes(app, settings.api_version)

    @app.on_event("startup")
    def _startup_auth_service() -> None:
        app.state.auth_service = build_auth_service(settings)

    @app.on_event("startup")
    def _startup_browser_auth_service() -> None:
        app.state.browser_auth_service = build_browser_auth_service(settings)

    @app.get("/health", include_in_schema=False)
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
