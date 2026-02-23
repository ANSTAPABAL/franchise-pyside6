from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / '.env')


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv('APP_ENV', 'dev')
    app_secret_key: str = os.getenv('APP_SECRET_KEY', 'PracticePyside6RylovSuperSecureKey_2026_123456')
    app_jwt_expire_minutes: int = int(os.getenv('APP_JWT_EXPIRE_MINUTES', '60'))

    db_host: str = os.getenv('DB_HOST', 'localhost')
    db_port: int = int(os.getenv('DB_PORT', '5432'))
    db_name: str = os.getenv('DB_NAME', 'pyside6practice')
    db_user: str = os.getenv('DB_USER', 'postgres')
    db_password: str = os.getenv('DB_PASSWORD', 'root')

    import_root: str = os.getenv('IMPORT_ROOT', '')


settings = Settings()

