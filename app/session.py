from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SessionState:
    user_id: str = ''
    full_name: str = ''
    email: str = ''
    role: str = ''
    token: str = ''
    photo_base64: str | None = None


session = SessionState()
