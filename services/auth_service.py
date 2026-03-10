"""сервис авторизации.

единственная задача — проверить логин/пароль и вернуть данные пользователя
для заполнения объекта session.
"""

from __future__ import annotations

from core.db import db_cursor
from core.security import create_access_token


def authenticate(email: str, password: str):
    """проверяет учётные данные и возвращает словарь с профилем пользователя.

    как работает:
    - ищем пользователя по email (регистр игнорируется через lower());
    - is_active = TRUE — заблокированные пользователи войти не смогут;
    - LEFT JOIN user_profiles — берём фото, даже если профиль не заполнен;
    - сравниваем пароль с полем password_plain (открытый текст, учебный вариант);
    - если всё ок — создаём jwt-токен и кладём в возвращаемый словарь.

    возвращает dict {id, full_name, email, role, photo_base64, token}
    или None, если данные неверные.
    """
    # только читаем, commit не нужен
    with db_cursor() as cur:
        cur.execute(
            '''
            SELECT u.id, u.full_name, u.email, u.role, u.password_plain, up.photo_base64
            FROM users u
            LEFT JOIN user_profiles up ON up.user_id = u.id
            WHERE lower(u.email) = lower(%s) AND u.is_active = TRUE
            ''',
            (email,),
        )
        row = cur.fetchone()

    # пользователь не найден или неактивен
    if not row:
        return None

    # пробуем оба поля на случай, если в бд хранится и хеш, и открытый пароль
    stored = (row.get('password_plain') or row.get('password_hash') or '').strip()
    if not stored or password != stored:
        return None  # пароль не совпал

    # данные верные — генерируем токен для сессии
    token = create_access_token(str(row['id']), row['role'])
    return {
        'id': str(row['id']),
        'full_name': row['full_name'],
        'email': row['email'],
        'role': row['role'],
        'photo_base64': row.get('photo_base64'),
        'token': token,
    }
