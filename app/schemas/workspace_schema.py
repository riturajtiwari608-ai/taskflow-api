from pydantic import BaseModel, Field
from typing import Optional


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)


class WorkspaceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner_id: int

    class Config:
        from_attributes = True