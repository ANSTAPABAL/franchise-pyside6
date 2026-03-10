"""централизованные настройки проекта.

читает переменные из .env и делает объект settings, который используется везде.
фишка: dataclass(frozen=True) — объект нельзя изменить после создания,
случайная перезапись настроек в рантайме невозможна.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# вычисляем корень проекта (папка выше core/) и грузим .env оттуда
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / '.env')


@dataclass(frozen=True)
class Settings:
    """конфигурация приложения и базы данных.

    фишка: os.getenv('KEY', 'default') — если переменная не задана в .env,
    используется значение по умолчанию. благодаря этому приложение
    запустится даже без .env-файла.
    """
    # среда: 'dev' или 'prod'
    app_env: str = os.getenv('APP_ENV', 'dev')

    # секретный ключ для подписи jwt-токенов
    app_secret_key: str = os.getenv('APP_SECRET_KEY', 'PracticePyside6RylovSuperSecureKey_2026_123456')

    # через сколько минут истекает токен
    app_jwt_expire_minutes: int = int(os.getenv('APP_JWT_EXPIRE_MINUTES', '60'))

    # параметры postgresql
    db_host: str = os.getenv('DB_HOST', 'localhost')
    db_port: int = int(os.getenv('DB_PORT', '5432'))
    db_name: str = os.getenv('DB_NAME', 'pyside6practice')
    db_user: str = os.getenv('DB_USER', 'postgres')
    db_password: str = os.getenv('DB_PASSWORD', 'root')

    # путь к папке с файлами для скрипта импорта
    import_root: str = os.getenv('IMPORT_ROOT', '')


# единственный экземпляр — импортируется во все модули
settings = Settings()
