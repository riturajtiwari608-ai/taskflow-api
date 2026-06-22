from pydantic import BaseModel, Field
from typing import Optional


class ProjectCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    workspace_id: int = Field(gt=0)


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    is_archived: Optional[bool] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    workspace_id: int
    is_archived: bool

    class Config:
        from_attributes = True