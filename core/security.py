"""утилиты безопасности: хеширование паролей и jwt-токены.

важно: в текущей версии логин проверяет поле password_plain (пароль в открытом виде).
функции bcrypt написаны на будущее, пока они не используются в authenticate().
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from core.settings import settings


def hash_password(password: str) -> str:
    """хешируем пароль через bcrypt и возвращаем строку хеша.

    фишка: gensalt() каждый раз создаёт новую случайную соль,
    поэтому даже одинаковые пароли дают разные хеши —
    защита от rainbow-таблиц.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """проверяем, совпадает ли открытый пароль с bcrypt-хешем.

    фишка: соль хранится прямо внутри хеша, bcrypt сам её извлекает —
    хранить соль отдельно не нужно.
    """
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def create_access_token(user_id: str, role: str) -> str:
    """создаём подписанный jwt-токен с id пользователя, ролью и временем жизни.

    фишка: токен подписан секретным ключом из settings.app_secret_key
    алгоритмом HS256. поле 'exp' — время истечения, сервер может проверить
    актуальность токена без обращения в бд.

    что внутри токена:
        sub  — user_id (чей токен)
        role — роль (admin / operator / viewer)
        iat  — когда выпущен
        exp  — когда истекает (iat + app_jwt_expire_minutes)
    """
    now = datetime.now(UTC)
    payload = {
        'sub': user_id,
        'role': role,
        'iat': now,
        'exp': now + timedelta(minutes=settings.app_jwt_expire_minutes),
    }
    # HS256 — симметричный алгоритм, один ключ и для подписи, и для проверки
    return jwt.encode(payload, settings.app_secret_key, algorithm='HS256')
