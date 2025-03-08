import mimetypes
import random
import uuid
from urllib.parse import quote

from moviepy import VideoFileClip
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import ffmpeg
from fastapi import HTTPException

from conf import UPLOAD_DIR, BASE_URL, LETTERS

BACKGROUND_COLORS = [
    ((230, 230, 230), (0, 0, 0)),  # Светлый серый
    ((220, 220, 220), (0, 0, 0)),  # Серый
    ((200, 200, 200), (0, 0, 0)),  # Тёмно-серый
    ((190, 190, 190), (0, 0, 0)),  # Стальной серый
    ((180, 180, 180), (0, 0, 0)),  # Графитовый
    ((160, 160, 160), (0, 0, 0)),  # Угольно-серый
    ((140, 140, 140), (255, 255, 255)),  # Тёмно-серый (белый текст)
    ((120, 120, 120), (255, 255, 255)),  # Антрацитовый
    ((100, 100, 100), (255, 255, 255)),  # Чёрный жемчуг
    ((80, 80, 80), (255, 255, 255)),  # Графитовый
    ((60, 60, 60), (255, 255, 255)),  # Темно-угольный
    ((40, 40, 40), (255, 255, 255)),  # Почти чёрный
    ((255, 239, 213), (0, 0, 0)),  # Персиковый
    ((255, 228, 196), (0, 0, 0)),  # Бежевый
    ((255, 218, 185), (0, 0, 0)),  # Песочный
    ((250, 235, 215), (0, 0, 0)),  # Античный белый
    ((255, 182, 193), (0, 0, 0)),  # Розовый
    ((255, 160, 122), (0, 0, 0)),  # Лососевый
    ((233, 150, 122), (0, 0, 0)),  # Персиково-оранжевый
    ((210, 180, 140), (0, 0, 0)),  # Светло-коричневый
    ((244, 164, 96), (0, 0, 0)),  # Тёмно-персиковый
    ((218, 165, 32), (0, 0, 0)),  # Золотистый
    ((184, 134, 11), (255, 255, 255)),  # Тёмно-золотистый
    ((189, 183, 107), (0, 0, 0)),  # Оливковый
    ((143, 188, 143), (0, 0, 0)),  # Тёмно-зелёный
    ((60, 179, 113), (0, 0, 0)),  # Средне-зелёный
    ((46, 139, 87), (255, 255, 255)),  # Морской волны
    ((102, 205, 170), (0, 0, 0)),  # Аквамариновый
    ((175, 238, 238), (0, 0, 0)),  # Голубоватый
    ((72, 209, 204), (0, 0, 0)),  # Бирюзовый
    ((0, 255, 255), (0, 0, 0)),  # Ярко-голубой
    ((70, 130, 180), (255, 255, 255)),  # Стальной синий
    ((100, 149, 237), (255, 255, 255)),  # Голубой Корнфлауэр
    ((30, 144, 255), (255, 255, 255)),  # Ярко-голубой
    ((25, 25, 112), (255, 255, 255)),  # Тёмно-синий
    ((123, 104, 238), (255, 255, 255)),  # Средний сланцевый синий
    ((72, 61, 139), (255, 255, 255)),  # Тёмно-фиолетовый
    ((255, 140, 0), (0, 0, 0)),  # Оранжевый
    ((255, 165, 0), (0, 0, 0)),  # Тёмно-оранжевый
    ((218, 112, 214), (0, 0, 0)),  # Орхидея
    ((199, 21, 133), (255, 255, 255)),  # Розово-фиолетовый
    ((255, 20, 147), (0, 0, 0)),  # Темно-розовый
    ((176, 224, 230), (0, 0, 0)),  # Светло-голубой
    ((173, 255, 47), (0, 0, 0)),  # Жёлто-зелёный
    ((124, 252, 0), (0, 0, 0)),  # Ярко-зелёный
    ((50, 205, 50), (0, 0, 0)),  # Лаймовый
    ((0, 255, 127), (0, 0, 0)),  # Весенне-зелёный
    ((47, 79, 79), (255, 255, 255)),  # Тёмный серо-зелёный
    ((119, 136, 153), (255, 255, 255)),  # Синий серый
]

import subprocess
from mutagen.mp3 import MP3
from mutagen.wave import WAVE


def get_audio_duration(file_path: str) -> float:
    """Определяет длительность аудиофайла (MP3, WAV)."""
    try:
        if file_path.endswith(".mp3"):
            audio = MP3(file_path)
        elif file_path.endswith(".wav"):
            audio = WAVE(file_path)
        else:
            return 0.0  # Если формат не поддерживается
        return round(audio.info.length, 2)
    except Exception as e:
        print(f"Ошибка определения длительности аудио: {e}")
        raise HTTPException(detail="При определении длительности аудио произошла ошибка", status_code=500)


def get_video_duration(file_path: str) -> float:
    """Определяет длительность видеофайла с помощью ffmpeg."""
    try:
        clip = VideoFileClip(file_path)
        duration = clip.duration
        clip.close()
        return duration
    except Exception as e:
        print(e)
        raise HTTPException(detail="При определении длительности видео произошла ошибка", status_code=500)


def generate_image_from_string(string, size, bg: tuple = None):
    if not string:
        raise ValueError("String cannot be empty")

    font = ImageFont.truetype("arial.ttf", size[0] / 2)
    if not bg:
        background, text_color = random.choice(BACKGROUND_COLORS)
    else:
        background, text_color = bg
    image = Image.new("RGB", size, background)
    draw = ImageDraw.Draw(image)

    text = string[0].upper()
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    text_x = (size[0] - text_width) // 2
    text_y = (size[1] - text_height) // 2.5

    draw.text((text_x, text_y), text, font=font, fill=text_color)

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    image_path = os.path.join(UPLOAD_DIR, f"{text}_{size[0]}x{size[1]}.jpg")
    image.save(image_path, format="JPEG")

    return image_path


def validate_file(file_path):
    file_size = os.path.getsize(file_path)
    mimetype = mimetypes.guess_type(file_path)[0]

    if mimetype and mimetype.startswith("audio"):
        if file_size > 100 * 1024 * 1024:
            return False, "Audio file size must not exceed 100MB"

    elif mimetype and mimetype.startswith("video"):
        if file_size > 1024 * 1024 * 1024:
            return False, "Video file size must not exceed 1GB"

        try:
            clip = VideoFileClip(file_path)
            duration = clip.duration
            clip.close()
            if duration > 90:
                return False, "Video duration must not exceed 1 minute 30 seconds"
        except Exception as e:
            print(e)
            return False, f"Could not determine video duration {e}"

    elif mimetype and mimetype.startswith("image"):
        if file_size > 50 * 1024 * 1024:
            return False, "Image file size must not exceed 50MB"
    else:
        return False, "File is not an image, video or audio"

    return True, "Valid file"


def resize_image(image_path: str, sizes: list[tuple], blur: list[int] = None):
    paths = {}
    new_path = None
    with Image.open(image_path) as img:
        for n, size in enumerate(sizes):
            max_width, max_height = size
            img_width, img_height = img.width, img.height

            if img_width < max_width and img_height < max_height:
                paths[f"{LETTERS[n]}"] = new_path or image_path
                continue

            aspect_ratio = img.width / img.height

            if img_width > img_height:
                new_width = max_width
                new_height = int(new_width / aspect_ratio)
            else:
                new_height = max_height
                new_width = int(new_height * aspect_ratio)

            img_resized = img.copy()
            img_resized.thumbnail((new_width, new_height))

            if blur and n < len(blur):  # Исправлено условие
                img_resized = img_resized.filter(ImageFilter.GaussianBlur(radius=blur[n]))
                new_path = os.path.join(
                    os.path.dirname(image_path), f"{uuid.uuid4().hex}_{new_width}x{new_height}_blurred.jpg")
            else:
                new_path = os.path.join(os.path.dirname(image_path), f"{uuid.uuid4().hex}_{new_width}x{new_height}.jpg")

            img_resized.save(new_path, "JPEG")
            paths[f"{LETTERS[n]}"] = get_file_url(new_path)

    os.remove(image_path)  # Удаляем оригинал
    return paths


def generate_video_preview(video_path: str):
    preview_path = f"{os.path.splitext(video_path)[0]}_preview.jpg"
    try:
        clip = VideoFileClip(video_path)
        frame = clip.get_frame(clip.duration / 2)  # Берём кадр из середины видео
        img = Image.fromarray(frame)
        img.thumbnail(clip.size)  # Сжимаем превью
        img.save(preview_path, format="JPEG", quality=50, optimize=True)
        clip.close()
        return preview_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating video preview: {str(e)}")


def get_file_url(file_path: str) -> str:
    """Приводит путь к файлу в корректный URL-формат."""
    relative_path = os.path.relpath(file_path, UPLOAD_DIR).replace("\\", "/")
    return f"{BASE_URL}/{quote(relative_path)}"
