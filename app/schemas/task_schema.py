from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

from app.constants.enums import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    description: Optional[str] = Field(default=None, max_length=1000)

    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.TODO

    due_date: Optional[date] = None

    project_id: int = Field(gt=0)
    assignee_id: Optional[int] = Field(default=None, gt=0)


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=150)
    description: Optional[str] = Field(default=None, max_length=1000)

    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None

    due_date: Optional[date] = None
    assignee_id: Optional[int] = Field(default=None, gt=0)


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: TaskPriority
    status: TaskStatus
    due_date: Optional[date]
    project_id: int
    assignee_id: Optional[int]
    created_by: int

    class Config:
        from_attributes = True