from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=1000)


class CommentUpdate(BaseModel):
    content: Optional[str] = Field(default=None, min_length=1, max_length=1000)


class CommentResponse(BaseModel):
    id: int
    content: str
    task_id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True