INSERT INTO payment_methods (code, name)
VALUES ('cash', 'Наличные'), ('card', 'Карта'), ('qr', 'QR')
ON CONFLICT (code) DO NOTHING;

INSERT INTO companies (name)
VALUES ('ООО Франчайзи 1'), ('ООО Франчайзи 2')
ON CONFLICT (name) DO NOTHING;

INSERT INTO users (full_name, email, phone, role, password_hash, is_active)
VALUES
    ('Иванов Иван Иванович', 'admin@franchise.local', '+7 (900) 000-00-01', 'admin',
     '$2b$12$fDU0AQszf4B5M4YBe6jXDe0KeP7JQOhI7xGp6m6l29Yfep6NX.NRa', TRUE),
    ('Петров Петр Петрович', 'operator@franchise.local', '+7 (900) 000-00-02', 'operator',
     '$2b$12$fDU0AQszf4B5M4YBe6jXDe0KeP7JQOhI7xGp6m6l29Yfep6NX.NRa', TRUE)
ON CONFLICT (email) DO NOTHING;

WITH c AS (SELECT id FROM companies ORDER BY name LIMIT 1),
a AS (SELECT id FROM users WHERE email='admin@franchise.local')
INSERT INTO vending_machines (
    company_id, name, location, model, machine_type, total_income,
    serial_number, inventory_number, manufacturer,
    manufacture_date, commissioned_date, created_date,
    last_verification_date, verification_interval_months, resource_hours,
    next_service_date, service_duration_hours, status,
    production_country, inventory_date, last_verifier_user_id, extra_status
)
SELECT
    c.id, 'ТА-Центр-001', 'ТЦ Север, вход 1', 'Necta Kikko', 'mixed', 1000,
    'SN-0001', 'INV-0001', 'Necta',
    CURRENT_DATE - INTERVAL '300 days', CURRENT_DATE - INTERVAL '200 days', CURRENT_DATE,
    CURRENT_DATE - INTERVAL '30 days', 12, 10000,
    CURRENT_DATE + INTERVAL '10 days', 4, 'working',
    'Россия', CURRENT_DATE - INTERVAL '5 days', a.id, 'attention'
FROM c, a
ON CONFLICT (serial_number) DO NOTHING;

INSERT INTO news (title, body)
VALUES
    ('Запуск нового франчайзи', 'Открыта новая точка в центральном офисном квартале.'),
    ('Плановая инвентаризация', 'Запланирована инвентаризация сети на текущую неделю.')
ON CONFLICT DO NOTHING;
