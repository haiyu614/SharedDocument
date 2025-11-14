from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean, func
from sqlalchemy.orm import relationship

from .base import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    current_version_id = Column(Integer, ForeignKey("document_versions.id"), nullable=True)
    is_archived = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="documents")
    versions = relationship(
        "DocumentVersion",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="DocumentVersion.version_number",
    )
    edit_logs = relationship("EditLog", back_populates="document", cascade="all, delete-orphan")

