from __future__ import annotations

from pathlib import Path
from urllib.parse import parse_qs

from argon2 import PasswordHasher
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.auth.repository import SqlAlchemyUserRepository
from app.auth.service import AuthService
from app.auth.tokens import AuthTokenService, InvalidTokenError
from app.core.db import create_database_engine, create_session_factory
from app.core.settings import get_settings

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter()


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request) -> HTMLResponse:
    settings = get_settings()
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "app_name": settings.app_name,
            "status": "walking skeleton ready",
            "health_url": f"/api/{settings.api_version}/health",
            "api_docs_url": f"/api/{settings.api_version}/docs",
        },
    )


def build_browser_auth_service(settings: object) -> AuthService:
    database_url = settings.database_url
    secret_key = settings.secret_key
    public_base_url = settings.public_base_url
    engine = create_database_engine(database_url)
    repository = SqlAlchemyUserRepository(
        engine=engine,
        session_factory=create_session_factory(engine),
    )
    repository.ensure_schema()
    return AuthService(
        repository=repository,
        password_hasher=PasswordHasher(),
        token_service=AuthTokenService(secret_key),
        public_base_url=public_base_url,
        email_sender=None,
    )


def _browser_auth_service(request: Request) -> AuthService:
    service = getattr(request.app.state, "browser_auth_service", None)
    if service is None:
        raise RuntimeError("browser auth service is not configured")
    return service


async def _read_urlencoded_form(request: Request) -> dict[str, str]:
    body = (await request.body()).decode("utf-8")
    parsed = parse_qs(body, keep_blank_values=True)
    return {key: values[-1] for key, values in parsed.items() if values}


@router.get("/verify-email", response_class=HTMLResponse, include_in_schema=False)
def verify_email(request: Request) -> HTMLResponse:
    settings = get_settings()

    state = "pending"
    heading = "Verify your email"
    message = "Open the email link and the page will verify your address automatically."
    verified_email = None

    return templates.TemplateResponse(
        request,
        "auth/verify_email.html",
        {
            "app_name": settings.app_name,
            "state": state,
            "heading": heading,
            "message": message,
            "verified_email": verified_email,
            "home_url": "/",
            "post_url": "/verify-email",
        },
    )


@router.post("/verify-email", response_class=HTMLResponse, include_in_schema=False)
async def verify_email_submit(request: Request) -> HTMLResponse:
    settings = get_settings()
    service = _browser_auth_service(request)
    fields = await _read_urlencoded_form(request)
    token = fields.get("token", "").strip()

    state = "success"
    heading = "Email verified"
    message = "Your email address has been activated. You can now sign in."
    verified_email = None

    if not token.strip():
        state = "error"
        heading = "Verification link missing"
        message = "The verification link did not include a token."
    else:
        try:
            verified_user = service.confirm_email_verification(token)
            verified_email = verified_user.email
        except InvalidTokenError:
            state = "error"
            heading = "Verification failed"
            message = "This link is invalid or has expired. Please request a new one."

    return templates.TemplateResponse(
        request,
        "auth/verify_email.html",
        {
            "app_name": settings.app_name,
            "state": state,
            "heading": heading,
            "message": message,
            "verified_email": verified_email,
            "home_url": "/",
            "post_url": "/verify-email",
            "token": token,
        },
    )


@router.get("/reset-password", response_class=HTMLResponse, include_in_schema=False)
def reset_password(request: Request) -> HTMLResponse:
    settings = get_settings()
    return templates.TemplateResponse(
        request,
        "auth/reset_password.html",
        {
            "app_name": settings.app_name,
            "state": "pending",
            "heading": "Reset your password",
            "message": "Choose a new password to finish resetting your account.",
            "home_url": "/",
            "post_url": "/reset-password",
        },
    )


@router.post("/reset-password", response_class=HTMLResponse, include_in_schema=False)
async def reset_password_submit(request: Request) -> HTMLResponse:
    settings = get_settings()
    service = _browser_auth_service(request)
    fields = await _read_urlencoded_form(request)
    token = fields.get("token", "").strip()
    new_password = fields.get("new_password", "").strip()

    state = "success"
    heading = "Password updated"
    message = "Your password has been updated. You can now sign in with the new password."
    if not token:
        state = "error"
        heading = "Reset link missing"
        message = "The reset link did not include a token."
    elif not new_password:
        state = "error"
        heading = "Missing password"
        message = "Please enter a new password."
    else:
        try:
            service.confirm_password_reset(token, new_password)
        except InvalidTokenError:
            state = "error"
            heading = "Reset failed"
            message = "This link is invalid or has expired. Please request a new one."

    return templates.TemplateResponse(
        request,
        "auth/reset_password.html",
        {
            "app_name": settings.app_name,
            "state": state,
            "heading": heading,
            "message": message,
            "home_url": "/",
            "post_url": "/reset-password",
            "token": token,
        },
    )
