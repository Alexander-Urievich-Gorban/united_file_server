import uuid
from sqlalchemy import (
    Column,
    String,
    Float,
    ForeignKey,
    DateTime,
    func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    api_key = Column(String, unique=True, nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    files = relationship(
        "MediaFile",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class MediaFile(Base):
    __tablename__ = "media_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    filename = Column(String, nullable=False, unique=True)
    original_name = Column(String, nullable=False)

    type = Column(String, nullable=False)  # image / video / audio
    duration = Column(Float, nullable=True)

    url = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="files")
