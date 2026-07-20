from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.exc import IntegrityError

from app.auth.repository import UserRecord
from app.auth.router import _current_user
from app.projects.repository import ProjectRecord
from app.projects.service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


class ProjectCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)

    @field_validator("name")
    @classmethod
    def _name_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("name must not be blank")
        return stripped


def _project_service(request: Request) -> ProjectService:
    service = getattr(request.app.state, "project_service", None)
    if service is None:
        raise RuntimeError("project service is not configured")
    return service


def _serialize_project(project: ProjectRecord) -> dict[str, Any]:
    return {
        "id": project.id,
        "name": project.name,
        "activeWorkflowVersionId": project.active_workflow_version_id,
        "activePolicyVersionId": project.active_policy_version_id,
    }


@router.get("")
def list_projects(request: Request) -> dict[str, Any]:
    actor: UserRecord = _current_user(request)
    service = _project_service(request)
    projects = service.list_accessible_projects(actor=actor)
    return {"items": [_serialize_project(project) for project in projects]}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_project(request: Request, payload: ProjectCreateRequest) -> dict[str, Any]:
    actor: UserRecord = _current_user(request)
    service = _project_service(request)
    try:
        project = service.create_project(name=payload.name, actor=actor)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="project already exists"
        ) from exc
    return _serialize_project(project)
