import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
BOOKS_DIR = DATA_DIR / 'books'
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///' + str(DATA_DIR / 'app.db'))
SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-for-prod')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '720'))
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin')

if not DATA_DIR.exists():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
if not BOOKS_DIR.exists():
    BOOKS_DIR.mkdir(parents=True, exist_ok=True)
