import os
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from conf import SERVER_ID, AVATAR_SIZES_STRINGS, UPLOAD_DIR, BASE_URL, LETTERS, SECRET
from main import app  # Импортируем FastAPI-приложение

TEST_FILES_DIR = "test_files"
UPLOADS_DIR = "uploads"
client = TestClient(app)


@pytest.fixture(scope="function")
def uploaded_files():
    """Фикстура для отслеживания загруженных во время теста файлов."""
    files = []
    yield files
    # Удаляем только файлы, загруженные во время теста
    for file_url in files:
        file_path = os.path.join(UPLOADS_DIR, os.path.basename(file_url))
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Ошибка при удалении {file_path}: {e}")

@pytest.mark.parametrize("filename, mime_type, expected_type", [
    ("image.jpg", "image/jpeg", "image"),
    ("audio.mp3", "audio/mpeg", "audio"),
    ("video.mp4", "video/mp4", "video"),
])
def test_upload_files(filename, mime_type, expected_type, uploaded_files):
    """Тестируем загрузку реальных файлов"""
    file_path = os.path.join(TEST_FILES_DIR, filename)
    assert os.path.exists(file_path), f"Файл {filename} отсутствует в {TEST_FILES_DIR}"

    with open(file_path, "rb") as file:
        files = {"file": (filename, file, mime_type)}
        response = client.post("/upload/file", files=files,headers={"SECRET":SECRET})

    assert response.status_code == 200
    data = response.json()
    assert data[0]["type"] == expected_type
    print("test_upload_files", data)
    # Добавляем загруженные файлы в список для последующего удаления
    if expected_type == 'video':
        for _, url in data[0]["urls"]['preview'].items():
            uploaded_files.append(url)

    for _, url in data[0]["urls"].items():
        if _ != 'preview':
            uploaded_files.append(url)


def test_create_blured(uploaded_files):
    """Тестируем создание размытого изображения"""
    file_path = os.path.join(TEST_FILES_DIR, "image.jpg")
    assert os.path.exists(file_path), "Файл image.jpg отсутствует в test_files"

    with open(file_path, "rb") as file:
        files = {"file": ("image.jpg", file, "image/jpeg")}
        response = client.post("/upload/file", files=files,headers={"SECRET":SECRET})

    assert response.status_code == 200
    data = response.json()
    assert data[0]["type"] == "image"
    print("test_create_blured", data)
    image_url = data[0]["urls"]["xl"]
    uploaded_files.extend(data[0]["urls"].values())
    # Сохраняем загруженные файлы
    uploaded_files.append(image_url)

    response = client.post("/blur_image", json={"url": image_url},headers={"SECRET":SECRET})

    assert response.status_code == 200
    data = response.json()
    assert "blurred_urls" in data
    print("blurred_urls", data)
    # Добавляем размытое изображение в список на удаление
    uploaded_files.extend(data["blurred_urls"].values())


def test_upload_avatar(uploaded_files):
    """Тестируем загрузку аватара"""
    file_path = os.path.join(TEST_FILES_DIR, "image.jpg")
    assert os.path.exists(file_path), "Файл image.jpg отсутствует в test_files"

    with open(file_path, "rb") as file:
        files = {"file": ("avatar.jpg", file, "image/jpeg")}
        response = client.post("/upload/avatar", files=files,headers={"SECRET":SECRET})

    assert response.status_code == 200
    data = response.json()
    print("test_upload_avatar", data)
    assert "result" in data

    # Сохраняем загруженный файл для удаления
    for _, v in data["result"]['urls'].items():
        uploaded_files.append(v)


def test_delete_files(uploaded_files):
    """Тестируем удаление загруженного файла"""
    file_to_delete = "video.mp4"
    file_path = os.path.join(UPLOADS_DIR, file_to_delete)

    if not os.path.exists(file_path):
        with open(os.path.join(TEST_FILES_DIR, file_to_delete), "rb") as file:
            files = {"file": (file_to_delete, file, "image/jpeg")}

            response = client.post("/upload/file", files=files,headers={"SECRET":SECRET})
            assert response.status_code == 200
            uploaded_files.append(response.json()[0]["urls"]["video"])
            uploaded_files.extend(response.json()[0]["urls"]["preview"].values())

    response = client.post("/delete_files", json={"urls": [file_path]},headers={"SECRET":SECRET})

    assert response.status_code == 200
    assert response.json() == {"message": "Files deleted successfully"}
    assert not os.path.exists(file_path), "Файл не был удалён"


def test_get_file(uploaded_files):
    """Тестируем скачивание загруженного файла"""
    file_path = os.path.join(TEST_FILES_DIR, "image.jpg")
    assert os.path.exists(file_path), "Файл image.jpg отсутствует в test_files"

    with open(file_path, "rb") as file:
        files = {"file": ("image.jpg", file, "image/jpeg")}
        response = client.post("/upload/file", files=files,headers={"SECRET":SECRET})
        assert response.status_code == 200

        image_url = response.json()[0]["urls"]["l"]
        uploaded_files.extend(response.json()[0]["urls"].values())

        filename = os.path.basename(image_url)

    response = client.get(f"{SERVER_ID}/files/{filename}")

    assert response.status_code == 200
    assert response.headers["content-type"] in ["image/jpeg", "image/png"]
    assert int(response.headers["content-length"]) > 0


@pytest.mark.parametrize("test_string", ["Але", "banana", "cherry"])
def test_image_from_string(test_string, uploaded_files):
    """Тестируем генерацию изображения из строки."""
    expected_filename = f"{test_string[0].upper()}"

    # Отправляем запрос
    response = client.post(f"/upload/from_string/{test_string}",headers={"SECRET":SECRET} )
    assert response.status_code == 200

    data = response.json()
    assert "result" in data
    assert data["result"]["file"] == expected_filename

    # Проверяем, что сгенерированы все файлы с правильными путями
    for n, size in enumerate(AVATAR_SIZES_STRINGS):
        expected_file_path = os.path.join(UPLOAD_DIR, f"{expected_filename}_{size}.jpg")
        expected_url = f"{BASE_URL}/{quote(expected_filename)}_{size}.jpg"

        # Приводим путь к универсальному формату
        assert data["result"]["urls"][LETTERS[n]].replace("\\", "/") == expected_url
        assert os.path.exists(expected_file_path), f"Файл {expected_file_path} не был создан"

