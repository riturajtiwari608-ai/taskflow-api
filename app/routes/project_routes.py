from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.workspace import Workspace
from app.models.project import Project
from app.schemas.project_schema import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse
)
from app.utils.security import get_current_user
from app.utils.permissions import (
    get_workspace_member,
    require_workspace_roles,
    get_project_with_access,
    require_project_roles
)

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


@router.post("/", response_model=ProjectResponse)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_workspace_roles(
        workspace_id=project_data.workspace_id,
        allowed_roles=["admin", "manager"],
        current_user=current_user,
        db=db
    )

    project = Project(
        name=project_data.name,
        description=project_data.description,
        workspace_id=project_data.workspace_id
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


@router.get("/", response_model=list[ProjectResponse])
def get_my_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_workspace_ids = [
        membership.workspace_id
        for membership in current_user_workspace_memberships(db, current_user)
    ]

    projects = db.query(Project).filter(
        Project.workspace_id.in_(user_workspace_ids)
    ).all()

    return projects


def current_user_workspace_memberships(db: Session, current_user: User):
    from app.models.workspace_member import WorkspaceMember

    return db.query(WorkspaceMember).filter(
        WorkspaceMember.user_id == current_user.id
    ).all()


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project, member = get_project_with_access(
        project_id=project_id,
        current_user=current_user,
        db=db
    )

    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project, member = require_project_roles(
        project_id=project_id,
        allowed_roles=["admin", "manager"],
        current_user=current_user,
        db=db
    )

    if project_data.name is not None:
        project.name = project_data.name

    if project_data.description is not None:
        project.description = project_data.description

    if project_data.is_archived is not None:
        project.is_archived = project_data.is_archived

    db.commit()
    db.refresh(project)

    return project


@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project, member = require_project_roles(
        project_id=project_id,
        allowed_roles=["admin"],
        current_user=current_user,
        db=db
    )

    db.delete(project)
    db.commit()

    return {"message": "Project deleted successfully"}