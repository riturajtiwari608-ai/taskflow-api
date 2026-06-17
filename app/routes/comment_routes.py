from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.workspace import Workspace
from app.models.project import Project
from app.models.task import Task
from app.models.comment import Comment
from app.schemas.comment_schema import (
    CommentCreate,
    CommentUpdate,
    CommentResponse
)
from app.utils.security import get_current_user


router = APIRouter(
    tags=["Comments"]
)


def check_task_access(task_id: int, db: Session, current_user: User):
    task = db.query(Task).join(Project).join(Workspace).filter(
        Task.id == task_id,
        Workspace.owner_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied"
        )

    return task


@router.post("/tasks/{task_id}/comments", response_model=CommentResponse)
def create_comment(
    task_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_task_access(task_id, db, current_user)

    comment = Comment(
        content=comment_data.content,
        task_id=task_id,
        user_id=current_user.id
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


@router.get("/tasks/{task_id}/comments", response_model=list[CommentResponse])
def get_task_comments(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_task_access(task_id, db, current_user)

    comments = db.query(Comment).filter(
        Comment.task_id == task_id
    ).order_by(Comment.created_at.desc()).all()

    return comments


@router.patch("/comments/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = db.query(Comment).join(Task).join(Project).join(Workspace).filter(
        Comment.id == comment_id,
        Workspace.owner_id == current_user.id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or access denied"
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can edit only your own comment"
        )

    if comment_data.content is not None:
        comment.content = comment_data.content

    db.commit()
    db.refresh(comment)

    return comment


@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = db.query(Comment).join(Task).join(Project).join(Workspace).filter(
        Comment.id == comment_id,
        Workspace.owner_id == current_user.id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or access denied"
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can delete only your own comment"
        )

    db.delete(comment)
    db.commit()

    return {"message": "Comment deleted successfully"}