from __future__ import annotations

from core.db import db_cursor
from core.security import create_access_token


def authenticate(email: str, password: str):
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

    if not row:
        return None
    stored = (row.get('password_plain') or row.get('password_hash') or '').strip()
    if not stored or password != stored:
        return None

    token = create_access_token(str(row['id']), row['role'])
    return {
        'id': str(row['id']),
        'full_name': row['full_name'],
        'email': row['email'],
        'role': row['role'],
        'photo_base64': row.get('photo_base64'),
        'token': token,
    }
