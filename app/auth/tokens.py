from __future__ import annotations

from dataclasses import dataclass, field

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer


@dataclass(frozen=True, slots=True)
class TokenClaims:
    user_id: str
    email: str


class InvalidTokenError(ValueError):
    pass


@dataclass(slots=True)
class AuthTokenService:
    secret_key: str
    email_verification_salt: str = "beembhai.email-verification"
    password_reset_salt: str = "beembhai.password-reset"
    _serializer: URLSafeTimedSerializer = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._serializer = URLSafeTimedSerializer(self.secret_key)

    def create_email_verification_token(self, *, user_id: str, email: str) -> str:
        return self._serializer.dumps(
            {"user_id": user_id, "email": email}, salt=self.email_verification_salt
        )

    def parse_email_verification_token(
        self, token: str, *, max_age_seconds: int = 3600
    ) -> TokenClaims:
        return self._parse_token(
            token, salt=self.email_verification_salt, max_age_seconds=max_age_seconds
        )

    def create_password_reset_token(self, *, user_id: str, email: str) -> str:
        return self._serializer.dumps(
            {"user_id": user_id, "email": email}, salt=self.password_reset_salt
        )

    def parse_password_reset_token(
        self, token: str, *, max_age_seconds: int = 3600
    ) -> TokenClaims:
        return self._parse_token(
            token, salt=self.password_reset_salt, max_age_seconds=max_age_seconds
        )

    def _parse_token(self, token: str, *, salt: str, max_age_seconds: int) -> TokenClaims:
        try:
            payload = self._serializer.loads(token, salt=salt, max_age=max_age_seconds)
        except (BadSignature, SignatureExpired) as exc:
            raise InvalidTokenError("invalid or expired token") from exc
        return TokenClaims(user_id=payload["user_id"], email=payload["email"])
