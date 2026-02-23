-- Колонка для отображения пароля в админке (учебный проект). Значение по умолчанию только в БД.
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_plain TEXT DEFAULT '123';
UPDATE users SET password_plain = '123' WHERE password_plain IS NULL;

-- Пароль по умолчанию только в БД (не хардкод в коде)
ALTER TABLE users ALTER COLUMN password_plain SET DEFAULT '123';
ALTER TABLE users ALTER COLUMN password_hash SET DEFAULT '123';
