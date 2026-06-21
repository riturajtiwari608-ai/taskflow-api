from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class ProjectMemberCreate(BaseModel):
    email: EmailStr


class ProjectMemberResponse(BaseModel):
    id: int
    project_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectMemberDetailResponse(BaseModel):
    id: int
    project_id: int
    user_id: int
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    created_at: datetime

    class Config:
        from_attributes = True