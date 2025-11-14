from __future__ import annotations

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import relationship

from .base import Base


class EditLog(Base):
    __tablename__ = "edit_logs"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    version_id = Column(Integer, ForeignKey("document_versions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    operation = Column(JSON, nullable=False)
    cursor_position = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("Document", back_populates="edit_logs")
    version = relationship("DocumentVersion", back_populates="edit_logs")
    user = relationship("User")

