from pydantic import BaseModel, EmailStr
from typing import Optional


class WorkspaceMemberCreate(BaseModel):
    email: EmailStr
    role: str = "member"


class WorkspaceMemberUpdate(BaseModel):
    role: str


class WorkspaceMemberResponse(BaseModel):
    id: int
    workspace_id: int
    user_id: int
    role: str

    class Config:
        from_attributes = True


class WorkspaceMemberDetailResponse(BaseModel):
    id: int
    workspace_id: int
    user_id: int
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: str

    class Config:
        from_attributes = True