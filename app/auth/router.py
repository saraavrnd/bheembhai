from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request, Response, status
from pydantic import BaseModel, ConfigDict, Field

from app.auth.repository import ADMIN_ROLE, UserRecord
from app.auth.service import AuthService
from app.auth.tokens import InvalidTokenError

router = APIRouter(prefix="/auth", tags=["Auth"])
me_router = APIRouter(tags=["Auth"])


class RegisterRequest(BaseModel):
    email: str = Field(min_length=3, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=12)


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=1)


class EmailVerifyRequest(BaseModel):
    token: str = Field(min_length=1)


class PasswordResetRequest(BaseModel):
    email: str = Field(min_length=3, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class PasswordResetConfirmRequest(BaseModel):
    token: str = Field(min_length=1)
    new_password: str = Field(alias="newPassword", min_length=12)

    model_config = ConfigDict(populate_by_name=True)


def _auth_service(request: Request) -> AuthService:
    service = getattr(request.app.state, "auth_service", None)
    if service is None:
        raise RuntimeError("auth service is not configured")
    return service


def _serialize_user(user: UserRecord) -> dict[str, Any]:
    return {
        "id": user.id,
        "email": user.email,
        "platformRole": "PLATFORM_ADMIN" if user.platform_role == ADMIN_ROLE else "STANDARD",
        "emailVerifiedAt": user.email_verified_at,
    }


def _current_user(request: Request) -> UserRecord:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not signed in")
    service = _auth_service(request)
    user = service.repository.find_by_id(user_id)
    if user is None:
        request.session.clear()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not signed in")
    return user


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(request: Request, payload: RegisterRequest) -> dict[str, Any]:
    service = _auth_service(request)
    result = service.register_user(email=payload.email, password=payload.password)
    if result.action == "skipped":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email already exists")
    return _serialize_user(result.user)


@router.post("/login")
def login(request: Request, payload: LoginRequest) -> dict[str, Any]:
    service = _auth_service(request)
    try:
        user = service.authenticate_user(email=payload.email, password=payload.password)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect email or password",
        ) from exc

    request.session["user_id"] = user.id
    return {"user": _serialize_user(user)}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request) -> Response:
    request.session.clear()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@me_router.get("/me")
def me(request: Request) -> dict[str, Any]:
    user = _current_user(request)
    return {"user": _serialize_user(user), "memberships": []}


@router.post("/email/verify", status_code=status.HTTP_204_NO_CONTENT)
def verify_email(request: Request, payload: EmailVerifyRequest) -> Response:
    service = _auth_service(request)
    try:
        service.confirm_email_verification(payload.token)
    except InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/password-reset/request", status_code=status.HTTP_204_NO_CONTENT)
def request_password_reset(request: Request, payload: PasswordResetRequest) -> Response:
    service = _auth_service(request)
    service.request_password_reset(payload.email)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/password-reset/confirm", status_code=status.HTTP_204_NO_CONTENT)
def confirm_password_reset(
    request: Request,
    payload: PasswordResetConfirmRequest,
) -> Response:
    service = _auth_service(request)
    try:
        service.confirm_password_reset(payload.token, payload.new_password)
    except InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
