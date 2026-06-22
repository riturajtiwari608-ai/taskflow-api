from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)

    token = Column(String, unique=True, index=True, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    is_used = Column(Boolean, default=False)

    expires_at = Column(DateTime(timezone=True), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")