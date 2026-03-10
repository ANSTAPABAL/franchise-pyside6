"""утилиты подключения к postgresql.

даёт два инструмента:
- get_connection() — просто открыть соединение;
- db_cursor() — контекстный менеджер, сам делает commit/rollback.
"""

from __future__ import annotations

from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor

from core.settings import settings


def get_connection():
    """открывает новое соединение с бд, параметры берёт из settings.

    фишка: ничего не хардкодится — всё из .env, поэтому менять хост/порт
    можно без правки кода.
    """
    return psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
    )


@contextmanager
def db_cursor(commit: bool = False):
    """безопасный контекст для работы с курсором.

    если commit=False (по умолчанию) — только читаем, ничего не сохраняем.
    если commit=True — после блока данные фиксируются в бд.
    если что-то пошло не так — автоматически откат (rollback), бд не ломается.
    соединение закрывается всегда, даже если была ошибка.

    как использовать:
        with db_cursor() as cur:            # select
        with db_cursor(commit=True) as cur: # insert/update/delete
    """
    conn = get_connection()
    try:
        # RealDictCursor — строки возвращаются как словари, удобнее кортежей
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            yield cur          # здесь выполняется код внутри блока with
        if commit:
            conn.commit()      # сохраняем изменения только если попросили
    except Exception:
        conn.rollback()        # откатываем всё при ошибке
        raise                  # пробрасываем ошибку дальше
    finally:
        conn.close()           # закрываем соединение в любом случае
