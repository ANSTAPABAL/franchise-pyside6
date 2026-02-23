CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    role TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    photo_base64 TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS payment_methods (
    id SMALLSERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS modems (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    modem_uid TEXT UNIQUE NOT NULL,
    provider TEXT,
    connection_type TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vending_machines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
    modem_id UUID REFERENCES modems(id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    model TEXT NOT NULL,
    machine_type TEXT NOT NULL,
    total_income NUMERIC(14,2) NOT NULL DEFAULT 0,
    serial_number TEXT NOT NULL,
    inventory_number TEXT NOT NULL,
    manufacturer TEXT NOT NULL,
    manufacture_date DATE NOT NULL,
    commissioned_date DATE NOT NULL,
    created_date DATE NOT NULL DEFAULT CURRENT_DATE,
    last_verification_date DATE NOT NULL,
    verification_interval_months INTEGER NOT NULL,
    next_verification_date DATE,
    resource_hours INTEGER NOT NULL,
    next_service_date DATE NOT NULL,
    service_duration_hours INTEGER NOT NULL,
    status TEXT NOT NULL,
    production_country TEXT NOT NULL,
    inventory_date DATE NOT NULL,
    last_verifier_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    extra_status TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    price NUMERIC(10,2) NOT NULL,
    min_stock INTEGER NOT NULL,
    sales_trend NUMERIC(10,2) NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS machine_stock (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    machine_id UUID NOT NULL REFERENCES vending_machines(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity_available INTEGER NOT NULL,
    UNIQUE (machine_id, product_id)
);

CREATE TABLE IF NOT EXISTS sales (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    machine_id UUID NOT NULL REFERENCES vending_machines(id) ON DELETE RESTRICT,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL,
    amount NUMERIC(12,2) NOT NULL,
    sold_at TIMESTAMPTZ NOT NULL,
    payment_method_id SMALLINT NOT NULL REFERENCES payment_methods(id)
);

CREATE TABLE IF NOT EXISTS maintenance_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    machine_id UUID NOT NULL REFERENCES vending_machines(id) ON DELETE CASCADE,
    maintenance_date DATE NOT NULL,
    work_description TEXT NOT NULL,
    issues TEXT,
    executor_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS machine_monitor_snapshot (
    machine_id UUID PRIMARY KEY REFERENCES vending_machines(id) ON DELETE CASCADE,
    load_percent NUMERIC(5,2) NOT NULL DEFAULT 0,
    cash_amount NUMERIC(12,2) NOT NULL DEFAULT 0,
    events TEXT,
    equipment_status TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS news (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    actor_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    entity_name TEXT NOT NULL,
    entity_id TEXT,
    details JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
