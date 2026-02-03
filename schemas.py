from typing import List, Dict, Optional
from pydantic import BaseModel, HttpUrl, Field
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    api_key: str


class UserOut(BaseModel):
    id: UUID
    api_key: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- REQUESTS ----------

class BlurRequest(BaseModel):
    url: HttpUrl


class DeleteFilesRequest(BaseModel):
    urls: List[HttpUrl] = Field(..., min_items=1)


# ---------- RESPONSES ----------

class ImageUrls(BaseModel):
    original: Optional[HttpUrl] = None
    sizes: Dict[str, HttpUrl]


class ImageUploadResponse(BaseModel):
    file: str
    type: str = "image"
    urls: Dict[str, HttpUrl]


class VideoUploadResponse(BaseModel):
    file: str
    type: str = "video"
    duration: float
    urls: Dict[str, HttpUrl]


class AudioUploadResponse(BaseModel):
    file: str
    type: str = "audio"
    duration: float
    urls: Dict[str, HttpUrl]


class BlurResponse(BaseModel):
    file: str
    blurred_urls: Dict[str, HttpUrl]


class AvatarUploadResponse(BaseModel):
    result: Dict[str, Dict[str, HttpUrl]]


class FromStringResponse(BaseModel):
    result: Dict[str, Dict[str, HttpUrl]]
