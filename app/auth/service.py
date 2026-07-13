from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol
from urllib.parse import quote

from argon2 import PasswordHasher
from sqlalchemy.exc import IntegrityError

from app.auth.repository import ADMIN_ROLE, STANDARD_ROLE, SqlAlchemyUserRepository, UserRecord
from app.auth.tokens import AuthTokenService, InvalidTokenError
from app.notifications.email import BrevoEmailSender, EmailMessage, EmailSender


class PasswordHasherProtocol(Protocol):
    def hash(self, password: str) -> str: ...


@dataclass(frozen=True, slots=True)
class UserMutationResult:
    user: UserRecord
    action: str
    verification_email_sent: bool = False
    skipped_reason: str | None = None


@dataclass(slots=True)
class AuthService:
    repository: SqlAlchemyUserRepository
    password_hasher: PasswordHasherProtocol
    token_service: AuthTokenService
    public_base_url: str
    email_sender: EmailSender | None = None

    def upsert_user(
        self,
        *,
        email: str,
        password: str,
        platform_role: str = STANDARD_ROLE,
    ) -> UserMutationResult:
        normalized_email = self._normalize_email(email)
        password_hash = self.password_hasher.hash(password)

        with self.repository.session_scope() as session:
            existing_user = self.repository.find_by_email_in_session(session, normalized_email)

            if existing_user is None:
                user = self.repository.create_user_in_session(
                    session,
                    email=normalized_email,
                    password_hash=password_hash,
                    platform_role=platform_role,
                    email_verified_at=None,
                )
                action = "created"
            else:
                user = self.repository.update_user_in_session(
                    session,
                    existing_user.id,
                    password_hash=password_hash,
                    platform_role=platform_role,
                )
                action = "updated"

            verification_email_sent = False
            if user.email_verified_at is None:
                token = self.token_service.create_email_verification_token(
                    user_id=user.id,
                    email=user.email,
                )
                self._send_verification_email(user, token)
                verification_email_sent = True

        return UserMutationResult(
            user=user,
            action=action,
            verification_email_sent=verification_email_sent,
        )

    def register_user(
        self,
        *,
        email: str,
        password: str,
    ) -> UserMutationResult:
        normalized_email = self._normalize_email(email)
        password_hash = self.password_hasher.hash(password)

        try:
            with self.repository.session_scope() as session:
                existing_user = self.repository.find_by_email_in_session(session, normalized_email)
                if existing_user is not None:
                    return UserMutationResult(
                        user=existing_user,
                        action="skipped",
                        skipped_reason="duplicate_email",
                    )

                user = self.repository.create_user_in_session(
                    session,
                    email=normalized_email,
                    password_hash=password_hash,
                    platform_role=STANDARD_ROLE,
                    email_verified_at=None,
                )
                token = self.token_service.create_email_verification_token(
                    user_id=user.id,
                    email=user.email,
                )
                self._send_verification_email(user, token)
        except IntegrityError:
            existing_user = self.repository.find_by_email(normalized_email)
            if existing_user is None:
                raise
            return UserMutationResult(
                user=existing_user,
                action="skipped",
                skipped_reason="duplicate_email",
            )

        return UserMutationResult(
            user=user,
            action="created",
            verification_email_sent=True,
        )

    def bootstrap_platform_admin(self, *, email: str, password: str) -> UserMutationResult:
        normalized_email = self._normalize_email(email)
        password_hash = self.password_hasher.hash(password)

        with self.repository.session_scope() as session:
            existing_admin = self.repository.find_first_admin_in_session(session)
            if existing_admin is not None:
                return UserMutationResult(
                    user=existing_admin,
                    action="skipped",
                    skipped_reason="platform_admin_exists",
                )

            user = self.repository.create_user_in_session(
                session,
                email=normalized_email,
                password_hash=password_hash,
                platform_role=ADMIN_ROLE,
                email_verified_at=None,
            )
            token = self.token_service.create_email_verification_token(
                user_id=user.id,
                email=user.email,
            )
            self._send_verification_email(user, token)

        return UserMutationResult(
            user=user,
            action="created",
            verification_email_sent=True,
        )

    def request_email_verification(self, email: str) -> bool:
        user = self.repository.find_by_email(email)
        if user is None or user.email_verified_at is not None:
            return False
        token = self.token_service.create_email_verification_token(
            user_id=user.id,
            email=user.email,
        )
        self._send_verification_email(user, token)
        return True

    def confirm_email_verification(self, token: str) -> UserRecord:
        claims = self.token_service.parse_email_verification_token(token)
        user = self.repository.find_by_id(claims.user_id)
        if user is None or self._normalize_email(user.email) != self._normalize_email(claims.email):
            raise InvalidTokenError("verification token does not match a user")
        return self.repository.update_user(
            user.id,
            email_verified_at=datetime.now(UTC),
        )

    def request_password_reset(self, email: str) -> bool:
        user = self.repository.find_by_email(email)
        if user is None or user.email_verified_at is None:
            return False
        token = self.token_service.create_password_reset_token(
            user_id=user.id,
            email=user.email,
        )
        self._send_password_reset_email(user, token)
        return True

    def confirm_password_reset(self, token: str, new_password: str) -> UserRecord:
        claims = self.token_service.parse_password_reset_token(token)
        user = self.repository.find_by_id(claims.user_id)
        if user is None or self._normalize_email(user.email) != self._normalize_email(claims.email):
            raise InvalidTokenError("password reset token does not match a user")
        return self.repository.update_user(
            user.id,
            password_hash=self.password_hasher.hash(new_password),
        )

    def _send_verification_email(self, user: UserRecord, token: str) -> None:
        if self.email_sender is None:
            raise ValueError("email sender is required for verification emails")
        verify_url = self._build_frontend_url("verify-email", token)
        self.email_sender.send(
            EmailMessage(
                to_email=user.email,
                subject="Verify your BeemBhai account",
                html_content=(
                    f"<p>Hello,</p><p>Please verify your account:</p>"
                    f'<p><a href="{verify_url}">{verify_url}</a></p>'
                ),
                text_content=f"Please verify your account: {verify_url}",
            )
        )

    def _send_password_reset_email(self, user: UserRecord, token: str) -> None:
        if self.email_sender is None:
            raise ValueError("email sender is required for password reset emails")
        reset_url = self._build_frontend_url("reset-password", token)
        self.email_sender.send(
            EmailMessage(
                to_email=user.email,
                subject="Reset your BeemBhai password",
                html_content=(
                    f"<p>Hello,</p><p>You can reset your password here:</p>"
                    f'<p><a href="{reset_url}">{reset_url}</a></p>'
                ),
                text_content=f"Reset your password: {reset_url}",
            )
        )

    def _build_frontend_url(self, path: str, token: str) -> str:
        return f"{self.public_base_url.rstrip('/')}/{path}#token={quote(token, safe='')}"

    @staticmethod
    def _normalize_email(email: str) -> str:
        return email.strip().lower()


def build_auth_service(
    settings: object,
    *,
    email_sender: EmailSender | None = None,
    password_hasher: PasswordHasherProtocol | None = None,
) -> AuthService:
    repository = SqlAlchemyUserRepository.from_database_url(settings.database_url)
    repository.ensure_schema()
    sender = email_sender if email_sender is not None else BrevoEmailSender.from_settings(settings)
    return AuthService(
        repository=repository,
        password_hasher=password_hasher or PasswordHasher(),
        token_service=AuthTokenService(settings.secret_key),
        public_base_url=settings.public_base_url,
        email_sender=sender,
    )
