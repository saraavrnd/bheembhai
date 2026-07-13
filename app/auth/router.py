from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.auth.repository import ADMIN_ROLE, UserRecord
from app.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


class RegisterRequest(BaseModel):
    email: str = Field(min_length=3, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=12)


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


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(request: Request, payload: RegisterRequest) -> dict[str, Any]:
    service = _auth_service(request)
    result = service.register_user(email=payload.email, password=payload.password)
    if result.action == "skipped":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email already exists")
    return _serialize_user(result.user)
