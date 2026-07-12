from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, String, func, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Mapped, Session, mapped_column, sessionmaker

from app.core.db import Base, create_database_engine, create_session_factory

ADMIN_ROLE = "admin"
STANDARD_ROLE = "standard"
_UNSET = object()


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    platform_role: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    email_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


@dataclass(frozen=True, slots=True)
class UserRecord:
    id: str
    email: str
    password_hash: str
    platform_role: str
    email_verified_at: datetime | None


@dataclass(slots=True)
class SqlAlchemyUserRepository:
    engine: Engine
    session_factory: sessionmaker[Session]

    @classmethod
    def from_database_url(cls, database_url: str) -> SqlAlchemyUserRepository:
        engine = create_database_engine(database_url)
        return cls(engine=engine, session_factory=create_session_factory(engine))

    def ensure_schema(self) -> None:
        Base.metadata.create_all(self.engine)

    def find_by_email(self, email: str) -> UserRecord | None:
        with self.session_factory() as session:
            return self.find_by_email_in_session(session, email)

    def find_by_id(self, user_id: str) -> UserRecord | None:
        with self.session_factory() as session:
            return self.find_by_id_in_session(session, user_id)

    def find_first_admin(self) -> UserRecord | None:
        with self.session_factory() as session:
            return self.find_first_admin_in_session(session)

    @contextmanager
    def session_scope(self) -> Iterator[Session]:
        with self.session_factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    def find_by_email_in_session(self, session: Session, email: str) -> UserRecord | None:
        normalized_email = self._normalize_email(email)
        user = session.execute(
            select(User).where(func.lower(User.email) == normalized_email)
        ).scalar_one_or_none()
        return self._to_record(user) if user is not None else None

    def find_by_id_in_session(self, session: Session, user_id: str) -> UserRecord | None:
        user = session.get(User, user_id)
        return self._to_record(user) if user is not None else None

    def find_first_admin_in_session(self, session: Session) -> UserRecord | None:
        user = session.execute(
            select(User)
            .where(User.platform_role == ADMIN_ROLE)
            .order_by(User.created_at.asc())
            .limit(1)
        ).scalar_one_or_none()
        return self._to_record(user) if user is not None else None

    def create_user(
        self,
        *,
        email: str,
        password_hash: str,
        platform_role: str = STANDARD_ROLE,
        email_verified_at: datetime | None = None,
    ) -> UserRecord:
        with self.session_scope() as session:
            return self.create_user_in_session(
                session,
                email=email,
                password_hash=password_hash,
                platform_role=platform_role,
                email_verified_at=email_verified_at,
            )

    def update_user(
        self,
        user_id: str,
        *,
        email: str | None = None,
        password_hash: str | None = None,
        platform_role: str | None = None,
        email_verified_at: datetime | object = _UNSET,
    ) -> UserRecord:
        with self.session_scope() as session:
            return self.update_user_in_session(
                session,
                user_id,
                email=email,
                password_hash=password_hash,
                platform_role=platform_role,
                email_verified_at=email_verified_at,
            )

    def create_user_in_session(
        self,
        session: Session,
        *,
        email: str,
        password_hash: str,
        platform_role: str = STANDARD_ROLE,
        email_verified_at: datetime | None = None,
    ) -> UserRecord:
        user = User(
            email=self._normalize_email(email),
            password_hash=password_hash,
            platform_role=platform_role,
            email_verified_at=email_verified_at,
        )
        session.add(user)
        session.flush()
        session.refresh(user)
        return self._to_record(user)

    def update_user_in_session(
        self,
        session: Session,
        user_id: str,
        *,
        email: str | None = None,
        password_hash: str | None = None,
        platform_role: str | None = None,
        email_verified_at: datetime | object = _UNSET,
    ) -> UserRecord:
        user = session.get(User, user_id)
        if user is None:
            raise LookupError(f"user not found: {user_id}")

        if email is not None:
            user.email = self._normalize_email(email)
        if password_hash is not None:
            user.password_hash = password_hash
        if platform_role is not None:
            user.platform_role = platform_role
        if email_verified_at is not _UNSET:
            user.email_verified_at = email_verified_at  # type: ignore[assignment]

        session.flush()
        session.refresh(user)
        return self._to_record(user)

    @staticmethod
    def _normalize_email(email: str) -> str:
        return email.strip().lower()

    @staticmethod
    def _to_record(user: User | None) -> UserRecord:
        if user is None:
            raise ValueError("user is required")
        return UserRecord(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash,
            platform_role=user.platform_role,
            email_verified_at=user.email_verified_at,
        )
