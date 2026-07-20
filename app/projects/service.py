from __future__ import annotations

from dataclasses import dataclass

from app.auth.repository import ADMIN_ROLE, UserRecord
from app.projects.repository import ProjectRecord, SqlAlchemyProjectRepository


@dataclass(slots=True)
class ProjectService:
    repository: SqlAlchemyProjectRepository

    def create_project(self, *, name: str, actor: UserRecord) -> ProjectRecord:
        if actor.platform_role != ADMIN_ROLE:
            raise PermissionError("only a platform admin may create a project")
        return self.repository.create_project(name=name)

    def list_accessible_projects(self, *, actor: UserRecord) -> list[ProjectRecord]:
        if actor.platform_role == ADMIN_ROLE:
            return self.repository.list_all()
        return self.repository.list_for_member(actor.id)


def build_project_service(settings: object) -> ProjectService:
    repository = SqlAlchemyProjectRepository.from_database_url(settings.database_url)
    repository.ensure_schema()
    return ProjectService(repository=repository)
