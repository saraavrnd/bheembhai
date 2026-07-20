from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.repository import ADMIN_ROLE, STANDARD_ROLE, UserRecord
from app.projects.repository import SqlAlchemyProjectRepository
from app.projects.service import ProjectService


def build_service() -> tuple[ProjectService, SqlAlchemyProjectRepository]:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    repository = SqlAlchemyProjectRepository(
        engine=engine,
        session_factory=sessionmaker(bind=engine, autoflush=False, expire_on_commit=False),
    )
    repository.ensure_schema()
    service = ProjectService(repository=repository)
    return service, repository


def admin_actor() -> UserRecord:
    return UserRecord(
        id="admin-1",
        email="admin@example.com",
        password_hash="hashed",
        platform_role=ADMIN_ROLE,
        email_verified_at=None,
    )


def standard_actor(user_id: str = "member-1") -> UserRecord:
    return UserRecord(
        id=user_id,
        email=f"{user_id}@example.com",
        password_hash="hashed",
        platform_role=STANDARD_ROLE,
        email_verified_at=None,
    )


def test_create_project_by_admin_persists_project_with_name_and_no_bindings() -> None:
    service, repository = build_service()

    created = service.create_project(name="Atlas", actor=admin_actor())

    stored = repository.list_all()
    assert len(stored) == 1
    assert stored[0].id == created.id
    assert stored[0].name == "Atlas"
    assert created.active_workflow_version_id is None
    assert created.active_policy_version_id is None


def test_create_project_rejects_non_admin_actor() -> None:
    service, repository = build_service()

    with pytest.raises(PermissionError):
        service.create_project(name="Atlas", actor=standard_actor())

    assert repository.list_all() == []


def test_list_accessible_projects_admin_sees_all_projects() -> None:
    service, _ = build_service()
    project_one = service.create_project(name="Atlas", actor=admin_actor())
    project_two = service.create_project(name="Zephyr", actor=admin_actor())

    accessible = service.list_accessible_projects(actor=admin_actor())

    assert {project.id for project in accessible} == {project_one.id, project_two.id}


def test_list_accessible_projects_member_sees_only_active_memberships() -> None:
    service, repository = build_service()
    accessible_project = service.create_project(name="Atlas", actor=admin_actor())
    hidden_project = service.create_project(name="Zephyr", actor=admin_actor())
    deactivated_project = service.create_project(name="Nimbus", actor=admin_actor())
    member = standard_actor("member-1")
    repository.create_membership(
        project_id=accessible_project.id,
        user_id=member.id,
        role="DEVELOPER",
        is_active=True,
    )
    repository.create_membership(
        project_id=deactivated_project.id,
        user_id=member.id,
        role="DEVELOPER",
        is_active=False,
    )

    accessible = service.list_accessible_projects(actor=member)

    accessible_ids = {project.id for project in accessible}
    assert accessible_ids == {accessible_project.id}
    assert hidden_project.id not in accessible_ids
    assert deactivated_project.id not in accessible_ids
