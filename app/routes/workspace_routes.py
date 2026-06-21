from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember
from app.schemas.workspace_schema import (
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceResponse
)
from app.schemas.workspace_member_schema import (
    WorkspaceMemberCreate,
    WorkspaceMemberUpdate,
    WorkspaceMemberResponse
)
from app.utils.security import get_current_user
from app.utils.permissions import (
    validate_role,
    get_workspace_member,
    require_workspace_roles
)

router = APIRouter(
    prefix="/workspaces",
    tags=["Workspaces"]
)


@router.post("/", response_model=WorkspaceResponse)
def create_workspace(
    workspace_data: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    workspace = Workspace(
        name=workspace_data.name,
        description=workspace_data.description,
        owner_id=current_user.id
    )

    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    admin_member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=current_user.id,
        role="admin"
    )

    db.add(admin_member)
    db.commit()

    return workspace


@router.get("/", response_model=list[WorkspaceResponse])
def get_my_workspaces(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    memberships = db.query(WorkspaceMember).filter(
        WorkspaceMember.user_id == current_user.id
    ).all()

    workspace_ids = [membership.workspace_id for membership in memberships]

    workspaces = db.query(Workspace).filter(
        Workspace.id.in_(workspace_ids)
    ).all()

    return workspaces


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_workspace_member(workspace_id, current_user, db)

    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id
    ).first()

    return workspace


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
def update_workspace(
    workspace_id: int,
    workspace_data: WorkspaceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_workspace_roles(
        workspace_id=workspace_id,
        allowed_roles=["admin"],
        current_user=current_user,
        db=db
    )

    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id
    ).first()

    if workspace_data.name is not None:
        workspace.name = workspace_data.name

    if workspace_data.description is not None:
        workspace.description = workspace_data.description

    db.commit()
    db.refresh(workspace)

    return workspace


@router.delete("/{workspace_id}")
def delete_workspace(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_workspace_roles(
        workspace_id=workspace_id,
        allowed_roles=["admin"],
        current_user=current_user,
        db=db
    )

    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id
    ).first()

    db.delete(workspace)
    db.commit()

    return {"message": "Workspace deleted successfully"}


@router.post("/{workspace_id}/members", response_model=WorkspaceMemberResponse)
def add_workspace_member(
    workspace_id: int,
    member_data: WorkspaceMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_workspace_roles(
        workspace_id=workspace_id,
        allowed_roles=["admin", "manager"],
        current_user=current_user,
        db=db
    )

    role = validate_role(member_data.role)

    user_to_add = db.query(User).filter(
        User.email == member_data.email
    ).first()

    if not user_to_add:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist"
        )

    existing_member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user_to_add.id
    ).first()

    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this workspace"
        )

    new_member = WorkspaceMember(
        workspace_id=workspace_id,
        user_id=user_to_add.id,
        role=role
    )

    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return new_member


@router.get("/{workspace_id}/members", response_model=list[WorkspaceMemberResponse])
def get_workspace_members(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_workspace_member(workspace_id, current_user, db)

    members = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id
    ).all()

    return members


@router.patch("/{workspace_id}/members/{user_id}", response_model=WorkspaceMemberResponse)
def update_workspace_member_role(
    workspace_id: int,
    user_id: int,
    member_data: WorkspaceMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_workspace_roles(
        workspace_id=workspace_id,
        allowed_roles=["admin"],
        current_user=current_user,
        db=db
    )

    role = validate_role(member_data.role)

    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user_id
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in this workspace"
        )

    member.role = role

    db.commit()
    db.refresh(member)

    return member


@router.delete("/{workspace_id}/members/{user_id}")
def remove_workspace_member(
    workspace_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_workspace_roles(
        workspace_id=workspace_id,
        allowed_roles=["admin"],
        current_user=current_user,
        db=db
    )

    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin cannot remove himself from workspace"
        )

    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user_id
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in this workspace"
        )

    db.delete(member)
    db.commit()

    return {"message": "Member removed successfully"}