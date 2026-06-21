from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.comment import Comment
from app.schemas.comment_schema import (
    CommentCreate,
    CommentUpdate,
    CommentResponse
)
from app.utils.security import get_current_user
from app.utils.permissions import get_task_with_access

router = APIRouter(
    tags=["Comments"]
)


@router.post("/tasks/{task_id}/comments", response_model=CommentResponse)
def create_comment(
    task_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_task_with_access(
        task_id=task_id,
        current_user=current_user,
        db=db
    )

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
    get_task_with_access(
        task_id=task_id,
        current_user=current_user,
        db=db
    )

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
    comment = db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    get_task_with_access(
        task_id=comment.task_id,
        current_user=current_user,
        db=db
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
    comment = db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    get_task_with_access(
        task_id=comment.task_id,
        current_user=current_user,
        db=db
    )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can delete only your own comment"
        )

    db.delete(comment)
    db.commit()

    return {"message": "Comment deleted successfully"}