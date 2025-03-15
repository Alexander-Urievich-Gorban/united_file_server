import mimetypes
import random
import uuid
from typing import List

import uvicorn

import shutil
import os
from urllib.parse import quote, unquote

from fastapi import FastAPI, UploadFile, File, HTTPException, Header, Depends
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from conf import UPLOAD_DIR, SERVER_ID, PHOTO_SIZES, PHOTO_BLURED, AVATAR_SIZES, AVATAR_SIZES_STRINGS, LETTERS, SECRET, PORT
from logs import ErrorLoggingMiddleware
from services import validate_file, generate_video_preview, resize_image, generate_image_from_string, BACKGROUND_COLORS, \
    get_file_url, get_audio_duration, get_video_duration

app = FastAPI()
app.add_middleware(ErrorLoggingMiddleware)

async def verify_secret(secret: str = Header(None)):
    """Проверка ключа в заголовке"""
    if secret != SECRET:
        raise HTTPException(status_code=403, detail="Invalid SECRET")
    return True
class BlurRequest(BaseModel):
    url: str


@app.post("/blur_image")
async def blur_image(data: BlurRequest, authorized: bool = Depends(verify_secret)):
    filename = os.path.basename(data.url)
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    valid, error = validate_file(file_path)
    if not valid:
        raise HTTPException(status_code=400, detail=error)

    blurred_urls = resize_image(file_path, PHOTO_SIZES, PHOTO_BLURED)

    return {"file": filename, "blurred_urls": blurred_urls}


@app.post("/upload/file")
async def upload_file(file: UploadFile = File(...), authorized: bool = Depends(verify_secret)):
    results = []
    ext = file.filename.split(".")[-1]
    file_type, _ = mimetypes.guess_type(file.filename)
    if not any((file_type.startswith("image"), file_type.startswith("video"), file_type.startswith("audio"))):
        raise HTTPException(detail=f"Invalid file type: {file_type}", status_code=400)
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    valid, error = validate_file(file_path)

    if not valid:
        results.append({"file": file.filename, "error": error})
        return results

    if file_type and file_type.startswith("image"):
        urls = resize_image(file_path, PHOTO_SIZES)
        results.append({"file": file.filename, "type": "image", "urls": urls})

    elif file_type and file_type.startswith("video"):
        preview = generate_video_preview(file_path)
        preview = resize_image(preview, PHOTO_SIZES)
        results.append({"file": file.filename,
                        "type": "video",
                        "duration": get_video_duration(file_path),
                        "urls": {"preview": preview,
                                 "video": get_file_url(file_path)}})

    elif file_type and file_type.startswith("audio"):
        results.append({"file": file.filename,
                        "type": "audio",
                        "duration":get_audio_duration(file_path),
                        "urls": {"audio": get_file_url(file_path)}})
    else:
        os.remove(file_path)  # Неизвестные файлы удаляем

    return results


@app.post("/upload/avatar")
async def upload_avatar(file: UploadFile = File(...), authorized: bool = Depends(verify_secret)):
    ext = file.filename.split(".")[-1]
    file_type, _ = mimetypes.guess_type(file.filename)

    if not file_type.startswith("image"):
        raise HTTPException(status_code=400, detail=f"file type is invalid, need image, current is {file_type}")

    unique_name = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    valid, error = validate_file(file_path)
    if not valid:
        raise HTTPException(status_code=400, detail=error)

    result = resize_image(file_path, AVATAR_SIZES)
    return {"result": {"urls": result}}


@app.post("/delete_files")
async def delete_files(data: dict, authorized: bool = Depends(verify_secret)):
    if "urls" not in data:
        raise HTTPException(status_code=400, detail="No file URLs provided")

    for url in data['urls']:
        filename = os.path.basename(unquote(url))
        print(filename)
        if len(filename) < 20:
            print("url len(url) < 10", filename)
            continue
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    return {"message": "Files deleted successfully"}


@app.get(f"/{SERVER_ID}/files/{{filename}}")
async def get_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, unquote(filename))

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, filename=unquote(filename))


@app.post("/upload/from_string/{string}")
async def image_from_string(string: str, authorized: bool = Depends(verify_secret)):
    filename = f"{string[0].upper()}"
    file_urls = {}
    bg = random.choice(BACKGROUND_COLORS)
    for n, size in enumerate(AVATAR_SIZES_STRINGS):
        path = os.path.join(UPLOAD_DIR, f"{filename}_{size}.jpg")
        if not os.path.exists(path):
            path = generate_image_from_string(string, AVATAR_SIZES[n], bg=bg)
        file_urls[f"{LETTERS[n]}"] = get_file_url(path)
    return {"result": {"file": filename, "urls": file_urls}}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORT)
