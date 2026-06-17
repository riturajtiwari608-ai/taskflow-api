from pydantic import BaseModel
from typing import Optional
from datetime import date


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    status: Optional[str] = "todo"
    due_date: Optional[date] = None
    project_id: int
    assignee_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[date] = None
    assignee_id: Optional[int] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: str
    status: str
    due_date: Optional[date]
    project_id: int
    assignee_id: Optional[int]
    created_by: int

    class Config:
        from_attributes = True