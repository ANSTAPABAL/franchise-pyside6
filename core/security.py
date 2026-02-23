from __future__ import annotations

from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from core.settings import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def create_access_token(user_id: str, role: str) -> str:
    now = datetime.now(UTC)
    payload = {
        'sub': user_id,
        'role': role,
        'iat': now,
        'exp': now + timedelta(minutes=settings.app_jwt_expire_minutes),
    }
    return jwt.encode(payload, settings.app_secret_key, algorithm='HS256')
