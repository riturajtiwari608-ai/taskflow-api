from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.workspace_member import WorkspaceMember
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.schemas.project_schema import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse
)
from app.schemas.project_member_schema import (
    ProjectMemberCreate,
    ProjectMemberResponse
)
from app.utils.security import get_current_user
from app.utils.permissions import (
    require_workspace_roles,
    get_project_with_access,
    require_project_roles,
    is_project_member
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

    project_member = ProjectMember(
        project_id=project.id,
        user_id=current_user.id
    )

    db.add(project_member)
    db.commit()

    return project


@router.get("/", response_model=list[ProjectResponse])
def get_my_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    memberships = db.query(WorkspaceMember).filter(
        WorkspaceMember.user_id == current_user.id
    ).all()

    admin_manager_workspace_ids = [
        membership.workspace_id
        for membership in memberships
        if membership.role in ["admin", "manager"]
    ]

    member_workspace_ids = [
        membership.workspace_id
        for membership in memberships
        if membership.role == "member"
    ]

    admin_manager_projects = db.query(Project).filter(
        Project.workspace_id.in_(admin_manager_workspace_ids)
    ).all()

    member_project_ids = [
        project_member.project_id
        for project_member in db.query(ProjectMember).filter(
            ProjectMember.user_id == current_user.id
        ).all()
    ]

    member_projects = db.query(Project).filter(
        Project.id.in_(member_project_ids),
        Project.workspace_id.in_(member_workspace_ids)
    ).all()

    all_projects = admin_manager_projects + member_projects

    unique_projects = {
        project.id: project
        for project in all_projects
    }

    return list(unique_projects.values())


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


@router.post("/{project_id}/members", response_model=ProjectMemberResponse)
def add_project_member(
    project_id: int,
    member_data: ProjectMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project, workspace_member = require_project_roles(
        project_id=project_id,
        allowed_roles=["admin", "manager"],
        current_user=current_user,
        db=db
    )

    user_to_add = db.query(User).filter(
        User.email == member_data.email
    ).first()

    if not user_to_add:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist"
        )

    target_workspace_member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == project.workspace_id,
        WorkspaceMember.user_id == user_to_add.id
    ).first()

    if not target_workspace_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be workspace member before adding to project"
        )

    existing_project_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_to_add.id
    ).first()

    if existing_project_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this project"
        )

    project_member = ProjectMember(
        project_id=project_id,
        user_id=user_to_add.id
    )

    db.add(project_member)
    db.commit()
    db.refresh(project_member)

    return project_member


@router.get("/{project_id}/members", response_model=list[ProjectMemberResponse])
def get_project_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_project_with_access(
        project_id=project_id,
        current_user=current_user,
        db=db
    )

    members = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id
    ).all()

    return members


@router.delete("/{project_id}/members/{user_id}")
def remove_project_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project, workspace_member = require_project_roles(
        project_id=project_id,
        allowed_roles=["admin", "manager"],
        current_user=current_user,
        db=db
    )

    project_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()

    if not project_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project member not found"
        )

    db.delete(project_member)
    db.commit()

    return {"message": "Project member removed successfully"}