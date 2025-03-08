import configparser
import os

config = configparser.ConfigParser()
config.read('conf.ini')

UPLOAD_DIR = "uploads"

SERVER_ID = config.get('settings', 'SERVER_ID')
LETTERS = ['s', 'm', 'l', 'xl']
PHOTO_SIZES = [(150, 150), (400, 400), (800, 800), (1920, 1080)]
PHOTO_BLURED = [10, 15, 20, 25]
AVATAR_SIZES = [(100, 100), (256, 256)]
AVATAR_SIZES_STRINGS = ("100x100", "256x256")
PORT = config.get('settings', 'PORT')
BASE_URL = f"http://127.0.0.1:{PORT}/{SERVER_ID}/files"  # Заменить на свой домен
SAVE_LOG_URL = config.get('settings', 'SAVE_LOG_URL')
LOG_SECRET = config.get('settings', 'LOG_SECRET')
SECRET = config.get('settings', 'SECRET')
"""uvicorn app:app --host 127.0.0.1 --port 5000
"""
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
