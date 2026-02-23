# Матрица трассировки требований

## БД и SQL-ограничения
- Уникальность `serial_number` и `inventory_number` реализована в `db/sql/002_constraints.sql` и триггере с русскими сообщениями.
- Правила дат и диапазонов реализованы `CHECK`-ограничениями в `db/sql/002_constraints.sql`.
- Расчет `next_verification_date` выполняется SQL-триггером `tr_vending_machine_validate_and_fill`.

## Авторизация и безопасность
- Хеширование паролей: `core/security.py` (`bcrypt`).
- JWT: `core/security.py` (`create_access_token`).
- Проверка credentials: `services/auth_service.py`.

## Главная
- 5 блоков дашборда и диаграммы: `app/pages/dashboard_page.py`.
- Данные блоков из SQL views: `db/sql/004_views.sql`.

## Администрирование
- ТА список/плитка, фильтр, пагинация, экспорт, действия: `app/pages/admin_machines_page.py`.
- CRUD сервисы и отвязка модема: `services/vending_service.py`.

## Монитор ТА
- Фильтры по кнопке, итоги и таблица: `app/pages/monitor_page.py` + `services/monitor_service.py`.

## Smoke
- Базовые smoke-тесты и чек-лист: `tests/smoke/*`, `docs/smoke_checklist.md`.
