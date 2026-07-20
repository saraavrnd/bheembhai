from __future__ import annotations

import re
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Mapped, Session, mapped_column, sessionmaker

from app.core.db import Base, create_database_engine, create_session_factory

_SLUG_INVALID_CHARS = re.compile(r"[^a-z0-9]+")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(280), unique=True, index=True, nullable=False)
    active_workflow_version_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    active_policy_version_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Membership(Base):
    __tablename__ = "memberships"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id"), index=True, nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), index=True, nullable=False
    )
    role: Mapped[str] = mapped_column(String(64), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


@dataclass(frozen=True, slots=True)
class ProjectRecord:
    id: str
    name: str
    slug: str
    active_workflow_version_id: str | None
    active_policy_version_id: str | None


@dataclass(frozen=True, slots=True)
class MembershipRecord:
    id: str
    project_id: str
    user_id: str
    role: str
    is_active: bool


@dataclass(slots=True)
class SqlAlchemyProjectRepository:
    engine: Engine
    session_factory: sessionmaker[Session]

    @classmethod
    def from_database_url(cls, database_url: str) -> SqlAlchemyProjectRepository:
        engine = create_database_engine(database_url)
        return cls(engine=engine, session_factory=create_session_factory(engine))

    def ensure_schema(self) -> None:
        Base.metadata.create_all(self.engine)

    @contextmanager
    def session_scope(self) -> Iterator[Session]:
        with self.session_factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    def list_all(self) -> list[ProjectRecord]:
        with self.session_factory() as session:
            return self.list_all_in_session(session)

    def list_for_member(self, user_id: str) -> list[ProjectRecord]:
        with self.session_factory() as session:
            return self.list_for_member_in_session(session, user_id)

    def create_project(self, *, name: str) -> ProjectRecord:
        with self.session_scope() as session:
            return self.create_project_in_session(session, name=name)

    def create_membership(
        self, *, project_id: str, user_id: str, role: str, is_active: bool = True
    ) -> MembershipRecord:
        with self.session_scope() as session:
            return self.create_membership_in_session(
                session, project_id=project_id, user_id=user_id, role=role, is_active=is_active
            )

    def list_all_in_session(self, session: Session) -> list[ProjectRecord]:
        projects = session.execute(select(Project).order_by(Project.created_at.asc())).scalars()
        return [self._to_record(project) for project in projects]

    def list_for_member_in_session(self, session: Session, user_id: str) -> list[ProjectRecord]:
        projects = session.execute(
            select(Project)
            .join(Membership, Membership.project_id == Project.id)
            .where(Membership.user_id == user_id, Membership.is_active.is_(True))
            .order_by(Project.created_at.asc())
        ).scalars()
        return [self._to_record(project) for project in projects]

    def create_project_in_session(self, session: Session, *, name: str) -> ProjectRecord:
        slug = self._unique_slug_in_session(session, name)
        project = Project(name=name, slug=slug)
        session.add(project)
        session.flush()
        session.refresh(project)
        return self._to_record(project)

    def create_membership_in_session(
        self,
        session: Session,
        *,
        project_id: str,
        user_id: str,
        role: str,
        is_active: bool = True,
    ) -> MembershipRecord:
        membership = Membership(
            project_id=project_id, user_id=user_id, role=role, is_active=is_active
        )
        session.add(membership)
        session.flush()
        session.refresh(membership)
        return self._to_membership_record(membership)

    def _unique_slug_in_session(self, session: Session, name: str) -> str:
        # Check-then-insert is not atomic: a concurrent create with the same name can pass this
        # check before either commits. That's fine — the DB unique constraint on `slug` is the
        # real guard, and the router maps the resulting IntegrityError to a 409 for the loser.
        base_slug = _SLUG_INVALID_CHARS.sub("-", name.strip().lower()).strip("-") or "project"
        slug = base_slug
        suffix = 1
        while (
            session.execute(select(Project.id).where(Project.slug == slug)).scalar_one_or_none()
            is not None
        ):
            suffix += 1
            slug = f"{base_slug}-{suffix}"
        return slug

    @staticmethod
    def _to_record(project: Project | None) -> ProjectRecord:
        if project is None:
            raise ValueError("project is required")
        return ProjectRecord(
            id=project.id,
            name=project.name,
            slug=project.slug,
            active_workflow_version_id=project.active_workflow_version_id,
            active_policy_version_id=project.active_policy_version_id,
        )

    @staticmethod
    def _to_membership_record(membership: Membership | None) -> MembershipRecord:
        if membership is None:
            raise ValueError("membership is required")
        return MembershipRecord(
            id=membership.id,
            project_id=membership.project_id,
            user_id=membership.user_id,
            role=membership.role,
            is_active=membership.is_active,
        )
