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

-- Товары для продаж и учёта
INSERT INTO products (name, description, price, min_stock, sales_trend)
VALUES
    ('Кофе Американо', 'Эспрессо с водой', 80.00, 5, 12.5),
    ('Капучино', 'Кофе с молоком', 120.00, 5, 18.0),
    ('Шоколад горячий', 'Горячий шоколад', 90.00, 3, 8.0),
    ('Печенье', 'Печенье в упаковке', 45.00, 2, 15.0),
    ('Вода 0.5', 'Питьевая вода', 50.00, 10, 25.0)
ON CONFLICT DO NOTHING;

-- Остатки по автомату (для учёта ТМЦ)
INSERT INTO machine_stock (machine_id, product_id, quantity_available)
SELECT m.id, p.id, 20 + (random() * 30)::int
FROM vending_machines m
CROSS JOIN products p
ON CONFLICT (machine_id, product_id) DO NOTHING;

-- Снимок монитора для отображения в Мониторе ТА
INSERT INTO machine_monitor_snapshot (machine_id, load_percent, cash_amount, events, equipment_status, updated_at)
SELECT id, 65.00, 12500.50, 'Нет событий', 'green', NOW()
FROM vending_machines
ON CONFLICT (machine_id) DO UPDATE SET
    load_percent = EXCLUDED.load_percent,
    cash_amount = EXCLUDED.cash_amount,
    events = EXCLUDED.events,
    equipment_status = EXCLUDED.equipment_status,
    updated_at = EXCLUDED.updated_at;

-- Продажи за последние 14 дней для динамики по quantity/amount (по сумме и по количеству)
INSERT INTO sales (machine_id, product_id, quantity, amount, sold_at, payment_method_id)
SELECT
    m.id,
    p.id,
    (1 + (random() * 4)::int),
    (1 + (random() * 4)::int) * p.price,
    (CURRENT_TIMESTAMP - (d.d || ' days')::interval + (random() * 14)::int * interval '1 hour'),
    (1 + floor(random() * 3)::int)::smallint
FROM vending_machines m
CROSS JOIN (SELECT id, price FROM products) p
CROSS JOIN generate_series(0, 13) AS d(d)
CROSS JOIN generate_series(1, 3) AS _(n);
