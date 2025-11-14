from __future__ import annotations

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import relationship

from .base import Base


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    diff_snapshot = Column(JSON, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("Document", back_populates="versions")
    author = relationship("User")
    edit_logs = relationship("EditLog", back_populates="version", cascade="all, delete-orphan")

