from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)

    is_archived = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    workspace = relationship("Workspace")