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
    urls: list[HttpUrl] = Field(..., min_items=1)


# ---------- RESPONSES ----------

class ImageUrls(BaseModel):
    original: HttpUrl | None = None
    sizes: dict[str, HttpUrl]


class ImageUploadResponse(BaseModel):
    file: str
    type: str = "image"
    urls: dict[str, HttpUrl]


class VideoUploadResponse(BaseModel):
    file: str
    type: str = "video"
    duration: float
    urls: dict[str, HttpUrl]


class AudioUploadResponse(BaseModel):
    file: str
    type: str = "audio"
    duration: float
    urls: dict[str, HttpUrl]


class BlurResponse(BaseModel):
    file: str
    blurred_urls: dict[str, HttpUrl]


class AvatarUploadResponse(BaseModel):
    result: dict[str, dict[str, HttpUrl]]


class FromStringResponse(BaseModel):
    result: dict[str, dict[str, HttpUrl]]
