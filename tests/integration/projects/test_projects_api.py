from __future__ import annotations

import os
from datetime import UTC, datetime
from uuid import uuid4

import httpx
from argon2 import PasswordHasher

from app.auth.repository import ADMIN_ROLE, STANDARD_ROLE, SqlAlchemyUserRepository, UserRecord
from app.projects.repository import SqlAlchemyProjectRepository

BASE_DATABASE_URL = "postgresql+psycopg://beembhai:beembhai@127.0.0.1:5432/beembhai"
_PASSWORD_HASHER = PasswordHasher()


def build_user_repository() -> SqlAlchemyUserRepository:
    database_url = os.getenv("TEST_DATABASE_URL", BASE_DATABASE_URL)
    repository = SqlAlchemyUserRepository.from_database_url(database_url)
    repository.ensure_schema()
    return repository


def build_project_repository() -> SqlAlchemyProjectRepository:
    database_url = os.getenv("TEST_DATABASE_URL", BASE_DATABASE_URL)
    repository = SqlAlchemyProjectRepository.from_database_url(database_url)
    repository.ensure_schema()
    return repository


def create_verified_user(
    repository: SqlAlchemyUserRepository, *, platform_role: str
) -> tuple[UserRecord, str]:
    email = f"user-{uuid4().hex[:8]}@example.com"
    password = "SignedInPassword123!"
    user = repository.create_user(
        email=email,
        password_hash=_PASSWORD_HASHER.hash(password),
        platform_role=platform_role,
        email_verified_at=datetime.now(UTC),
    )
    return user, password


def login(deployed_api: str, *, email: str, password: str) -> httpx.Client:
    client = httpx.Client(base_url=deployed_api, timeout=10.0)
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return client


def test_create_project_endpoint_returns_201_and_persists_project_for_admin(
    deployed_api: str,
) -> None:
    user_repository = build_user_repository()
    project_repository = build_project_repository()
    admin, password = create_verified_user(user_repository, platform_role=ADMIN_ROLE)
    client = login(deployed_api, email=admin.email, password=password)

    response = client.post("/api/v1/projects", json={"name": "Atlas"})

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Atlas"
    assert body["activeWorkflowVersionId"] is None
    assert body["activePolicyVersionId"] is None
    stored = [project for project in project_repository.list_all() if project.id == body["id"]]
    assert len(stored) == 1
    assert stored[0].name == "Atlas"


def test_create_project_endpoint_rejects_non_admin(deployed_api: str) -> None:
    member, password = create_verified_user(build_user_repository(), platform_role=STANDARD_ROLE)
    client = login(deployed_api, email=member.email, password=password)

    response = client.post("/api/v1/projects", json={"name": "Atlas"})

    assert response.status_code == 403


def test_create_project_endpoint_rejects_unauthenticated_request(deployed_api: str) -> None:
    response = httpx.post(
        f"{deployed_api}/api/v1/projects",
        json={"name": "Atlas"},
        timeout=10.0,
    )

    assert response.status_code == 401


def test_create_project_endpoint_rejects_missing_name(deployed_api: str) -> None:
    project_repository = build_project_repository()
    admin, password = create_verified_user(build_user_repository(), platform_role=ADMIN_ROLE)
    client = login(deployed_api, email=admin.email, password=password)
    before_count = len(project_repository.list_all())

    omitted_field_response = client.post("/api/v1/projects", json={})
    empty_name_response = client.post("/api/v1/projects", json={"name": ""})

    assert omitted_field_response.status_code == 422
    assert empty_name_response.status_code == 422
    assert len(project_repository.list_all()) == before_count


def test_create_project_endpoint_rejects_whitespace_only_name(deployed_api: str) -> None:
    project_repository = build_project_repository()
    admin, password = create_verified_user(build_user_repository(), platform_role=ADMIN_ROLE)
    client = login(deployed_api, email=admin.email, password=password)
    before_count = len(project_repository.list_all())

    response = client.post("/api/v1/projects", json={"name": "   "})

    assert response.status_code == 422
    assert len(project_repository.list_all()) == before_count


def test_create_project_endpoint_rejects_name_exceeding_max_length(deployed_api: str) -> None:
    project_repository = build_project_repository()
    admin, password = create_verified_user(build_user_repository(), platform_role=ADMIN_ROLE)
    client = login(deployed_api, email=admin.email, password=password)
    before_count = len(project_repository.list_all())

    response = client.post("/api/v1/projects", json={"name": "A" * 256})

    assert response.status_code == 422
    assert len(project_repository.list_all()) == before_count


def test_list_projects_endpoint_returns_only_accessible_projects(deployed_api: str) -> None:
    project_repository = build_project_repository()
    member, member_password = create_verified_user(
        build_user_repository(), platform_role=STANDARD_ROLE
    )

    accessible_project_one = project_repository.create_project(name=f"Atlas-{uuid4().hex[:6]}")
    accessible_project_two = project_repository.create_project(name=f"Borealis-{uuid4().hex[:6]}")
    hidden_project = project_repository.create_project(name=f"Zephyr-{uuid4().hex[:6]}")
    project_repository.create_membership(
        project_id=accessible_project_one.id,
        user_id=member.id,
        role="DEVELOPER",
        is_active=True,
    )
    project_repository.create_membership(
        project_id=accessible_project_two.id,
        user_id=member.id,
        role="REVIEWER",
        is_active=True,
    )

    client = login(deployed_api, email=member.email, password=member_password)
    response = client.get("/api/v1/projects")

    assert response.status_code == 200
    project_ids = {item["id"] for item in response.json()["items"]}
    assert project_ids == {accessible_project_one.id, accessible_project_two.id}
    assert hidden_project.id not in project_ids


def test_list_projects_endpoint_rejects_unauthenticated_request(deployed_api: str) -> None:
    response = httpx.get(f"{deployed_api}/api/v1/projects", timeout=10.0)

    assert response.status_code == 401
