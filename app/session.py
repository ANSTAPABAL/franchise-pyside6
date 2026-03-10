"""глобальное состояние текущей пользовательской сессии.

после успешного логина данные пользователя кладутся в объект `session`,
и все страницы ui читают их оттуда — не нужно каждый раз лезть в бд.

фишка: это паттерн «глобальное состояние» (singleton через модуль).
объект session один на всё приложение, импортируется напрямую:
    from app.session import session
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SessionState:
    """dto (data transfer object) с данными авторизованного пользователя.

    поля сбрасываются в пустые строки при инициализации —
    до входа они пустые, после логина заполняются в login_dialog.py.
    """
    user_id: str = ''       # uuid пользователя из бд
    full_name: str = ''     # полное имя (фамилия имя отчество)
    email: str = ''         # email для отображения в профиле
    role: str = ''          # роль: admin / operator / viewer
    token: str = ''         # jwt-токен (пока для будущего использования)
    photo_base64: str | None = None  # фото пользователя в base64 (может не быть)


# единственный экземпляр — импортируется во все модули
session = SessionState()
