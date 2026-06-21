from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.task import Task


VALID_ROLES = ["admin", "manager", "member"]


def validate_role(role: str):
    role = role.lower()

    if role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Role must be admin, manager, or member"
        )

    return role


def get_workspace_or_404(workspace_id: int, db: Session):
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id
    ).first()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    return workspace


def get_workspace_member(
    workspace_id: int,
    current_user: User,
    db: Session
):
    workspace = get_workspace_or_404(workspace_id, db)

    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == current_user.id
    ).first()

    if not member and workspace.owner_id == current_user.id:
        member = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=current_user.id,
            role="admin"
        )
        db.add(member)
        db.commit()
        db.refresh(member)

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace"
        )

    return member


def require_workspace_roles(
    workspace_id: int,
    allowed_roles: list[str],
    current_user: User,
    db: Session
):
    member = get_workspace_member(workspace_id, current_user, db)

    if member.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )

    return member


def get_project_or_404(project_id: int, db: Session):
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return project


def is_project_member(project_id: int, user_id: int, db: Session) -> bool:
    project_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()

    return project_member is not None


def get_project_with_access(
    project_id: int,
    current_user: User,
    db: Session
):
    project = get_project_or_404(project_id, db)

    workspace_member = get_workspace_member(
        workspace_id=project.workspace_id,
        current_user=current_user,
        db=db
    )

    if workspace_member.role in ["admin", "manager"]:
        return project, workspace_member

    if not is_project_member(project_id, current_user.id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project"
        )

    return project, workspace_member


def require_project_roles(
    project_id: int,
    allowed_roles: list[str],
    current_user: User,
    db: Session
):
    project = get_project_or_404(project_id, db)

    workspace_member = get_workspace_member(
        workspace_id=project.workspace_id,
        current_user=current_user,
        db=db
    )

    if workspace_member.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )

    return project, workspace_member


def get_task_with_access(
    task_id: int,
    current_user: User,
    db: Session
):
    task = db.query(Task).filter(
        Task.id == task_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    project, workspace_member = get_project_with_access(
        project_id=task.project_id,
        current_user=current_user,
        db=db
    )

    return task, project, workspace_member


def require_task_roles(
    task_id: int,
    allowed_roles: list[str],
    current_user: User,
    db: Session
):
    task = db.query(Task).filter(
        Task.id == task_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    project = get_project_or_404(task.project_id, db)

    workspace_member = get_workspace_member(
        workspace_id=project.workspace_id,
        current_user=current_user,
        db=db
    )

    if workspace_member.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )

    return task, project, workspace_member