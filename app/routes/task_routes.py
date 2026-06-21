from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.workspace_member import WorkspaceMember
from app.models.project import Project
from app.models.task import Task
from app.schemas.task_schema import (
    TaskCreate,
    TaskUpdate,
    TaskResponse
)
from app.utils.security import get_current_user
from app.utils.permissions import (
    require_project_roles,
    get_task_with_access,
    require_task_roles
)

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


@router.post("/", response_model=TaskResponse)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_project_roles(
        project_id=task_data.project_id,
        allowed_roles=["admin", "manager"],
        current_user=current_user,
        db=db
    )

    task = Task(
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        status=task_data.status,
        due_date=task_data.due_date,
        project_id=task_data.project_id,
        assignee_id=task_data.assignee_id,
        created_by=current_user.id
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


@router.get("/", response_model=list[TaskResponse])
def get_tasks(
    project_id: Optional[int] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    priority: Optional[str] = None,
    assignee_id: Optional[int] = None,
    due_date: Optional[date] = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    memberships = db.query(WorkspaceMember).filter(
        WorkspaceMember.user_id == current_user.id
    ).all()

    workspace_ids = [membership.workspace_id for membership in memberships]

    query = db.query(Task).join(Project).filter(
        Project.workspace_id.in_(workspace_ids)
    )

    if project_id:
        query = query.filter(Task.project_id == project_id)

    if status_filter:
        query = query.filter(Task.status == status_filter)

    if priority:
        query = query.filter(Task.priority == priority)

    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)

    if due_date:
        query = query.filter(Task.due_date == due_date)

    offset = (page - 1) * limit

    tasks = query.offset(offset).limit(limit).all()

    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task, project, member = get_task_with_access(
        task_id=task_id,
        current_user=current_user,
        db=db
    )

    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task, project, member = require_task_roles(
        task_id=task_id,
        allowed_roles=["admin", "manager"],
        current_user=current_user,
        db=db
    )

    if task_data.title is not None:
        task.title = task_data.title

    if task_data.description is not None:
        task.description = task_data.description

    if task_data.priority is not None:
        task.priority = task_data.priority

    if task_data.status is not None:
        task.status = task_data.status

    if task_data.due_date is not None:
        task.due_date = task_data.due_date

    if task_data.assignee_id is not None:
        task.assignee_id = task_data.assignee_id

    db.commit()
    db.refresh(task)

    return task


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task, project, member = require_task_roles(
        task_id=task_id,
        allowed_roles=["admin"],
        current_user=current_user,
        db=db
    )

    db.delete(task)
    db.commit()

    return {"message": "Task deleted successfully"}