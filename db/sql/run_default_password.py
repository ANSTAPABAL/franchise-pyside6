"""Один раз: установить DEFAULT '123' для паролей в БД."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from core.db import get_connection

conn = get_connection()
conn.autocommit = True
cur = conn.cursor()
cur.execute("ALTER TABLE users ALTER COLUMN password_plain SET DEFAULT '123'")
cur.execute("ALTER TABLE users ALTER COLUMN password_hash SET DEFAULT '123'")
print("OK: DEFAULT 123 установлен в БД для password_plain и password_hash")
cur.close()
conn.close()
