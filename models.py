import uuid
from sqlalchemy import Column, String, Float, Enum
from sqlalchemy.dialects.postgresql import UUID
from database import Base


class FileTypeEnum(str):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"


class MediaFile(Base):
    __tablename__ = "media_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False, unique=True)
    original_name = Column(String, nullable=False)

    type = Column(String, nullable=False)
    duration = Column(Float, nullable=True)

    url = Column(String, nullable=False)
