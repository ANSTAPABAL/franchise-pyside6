from __future__ import annotations

from core.db import db_cursor


def list_companies() -> list[dict]:
    with db_cursor() as cur:
        cur.execute('SELECT id, name, created_at FROM companies ORDER BY name')
        return [dict(r) for r in cur.fetchall()]


def add_company(name: str) -> None:
    with db_cursor(commit=True) as cur:
        cur.execute('INSERT INTO companies(name) VALUES (%s) ON CONFLICT (name) DO NOTHING', (name,))


def delete_company(company_id: str) -> None:
    with db_cursor(commit=True) as cur:
        cur.execute('DELETE FROM companies WHERE id = %s', (company_id,))


def list_users() -> list[dict]:
    with db_cursor() as cur:
        cur.execute(
            'SELECT id, full_name, email, phone, role, is_active, password_plain FROM users ORDER BY created_at DESC'
        )
        return [dict(r) for r in cur.fetchall()]


def add_user(full_name: str, email: str, phone: str, role: str, password: str | None = None) -> None:
    """Новый пользователь: пароль берётся из DEFAULT в БД (123), либо передан явно."""
    with db_cursor(commit=True) as cur:
        if password is not None:
            cur.execute(
                'INSERT INTO users(full_name, email, phone, role, password_hash, is_active, password_plain) VALUES (%s, %s, %s, %s, %s, TRUE, %s)',
                (full_name, email, phone, role, password, password),
            )
        else:
            cur.execute(
                'INSERT INTO users(full_name, email, phone, role, is_active) VALUES (%s, %s, %s, %s, TRUE)',
                (full_name, email, phone, role),
            )


def update_user(user_id: str, full_name: str, email: str, phone: str, role: str, is_active: bool) -> None:
    with db_cursor(commit=True) as cur:
        cur.execute(
            'UPDATE users SET full_name = %s, email = %s, phone = %s, role = %s, is_active = %s WHERE id = %s',
            (full_name, email, phone, role, is_active, user_id),
        )


def delete_user(user_id: str) -> None:
    with db_cursor(commit=True) as cur:
        cur.execute('DELETE FROM users WHERE id = %s', (user_id,))


def list_modems() -> list[dict]:
    with db_cursor() as cur:
        cur.execute('SELECT id, modem_uid, provider, connection_type, created_at FROM modems ORDER BY created_at DESC')
        return [dict(r) for r in cur.fetchall()]


def add_modem(modem_uid: str, provider: str, connection_type: str) -> None:
    with db_cursor(commit=True) as cur:
        cur.execute(
            'INSERT INTO modems(modem_uid, provider, connection_type) VALUES (%s, %s, %s) ON CONFLICT (modem_uid) DO NOTHING',
            (modem_uid, provider, connection_type),
        )


def delete_modem(modem_id: str) -> None:
    with db_cursor(commit=True) as cur:
        cur.execute('DELETE FROM modems WHERE id = %s', (modem_id,))


def list_news() -> list[dict]:
    with db_cursor() as cur:
        cur.execute('SELECT id, title, body, created_at FROM news ORDER BY created_at DESC LIMIT 50')
        return [dict(r) for r in cur.fetchall()]


def add_news(title: str, body: str) -> None:
    with db_cursor(commit=True) as cur:
        cur.execute('INSERT INTO news(title, body) VALUES (%s, %s)', (title, body))


def delete_news(news_id: str) -> None:
    with db_cursor(commit=True) as cur:
        cur.execute('DELETE FROM news WHERE id = %s', (news_id,))
