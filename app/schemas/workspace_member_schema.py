from pydantic import BaseModel, EmailStr
from typing import Optional

from app.constants.enums import UserRole


class WorkspaceMemberCreate(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.MEMBER


class WorkspaceMemberUpdate(BaseModel):
    role: UserRole


class WorkspaceMemberResponse(BaseModel):
    id: int
    workspace_id: int
    user_id: int
    role: UserRole

    class Config:
        from_attributes = True


class WorkspaceMemberDetailResponse(BaseModel):
    id: int
    workspace_id: int
    user_id: int
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: UserRole

    class Config:
        from_attributes = True