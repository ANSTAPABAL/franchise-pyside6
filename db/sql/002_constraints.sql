DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_vending_machines_serial') THEN
        ALTER TABLE vending_machines ADD CONSTRAINT uq_vending_machines_serial UNIQUE (serial_number);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_vending_machines_inventory') THEN
        ALTER TABLE vending_machines ADD CONSTRAINT uq_vending_machines_inventory UNIQUE (inventory_number);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_total_income_non_negative') THEN
        ALTER TABLE vending_machines ADD CONSTRAINT chk_total_income_non_negative CHECK (total_income >= 0);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_resource_hours_positive') THEN
        ALTER TABLE vending_machines ADD CONSTRAINT chk_resource_hours_positive CHECK (resource_hours > 0);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_service_duration_range') THEN
        ALTER TABLE vending_machines ADD CONSTRAINT chk_service_duration_range CHECK (service_duration_hours BETWEEN 1 AND 20);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_verification_interval_positive') THEN
        ALTER TABLE vending_machines ADD CONSTRAINT chk_verification_interval_positive CHECK (verification_interval_months > 0);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_machine_type') THEN
        ALTER TABLE vending_machines ADD CONSTRAINT chk_machine_type CHECK (machine_type IN ('card', 'cash', 'mixed'));
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_machine_status') THEN
        ALTER TABLE vending_machines ADD CONSTRAINT chk_machine_status CHECK (status IN ('working', 'broken', 'maintenance'));
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_inventory_date_range') THEN
        ALTER TABLE vending_machines ADD CONSTRAINT chk_inventory_date_range CHECK (inventory_date >= manufacture_date AND inventory_date <= CURRENT_DATE);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_last_verification_range') THEN
        ALTER TABLE vending_machines ADD CONSTRAINT chk_last_verification_range CHECK (last_verification_date >= manufacture_date AND last_verification_date <= CURRENT_DATE);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_commissioned_range') THEN
        ALTER TABLE vending_machines ADD CONSTRAINT chk_commissioned_range CHECK (commissioned_date >= manufacture_date AND commissioned_date <= created_date);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_next_service_after_created') THEN
        ALTER TABLE vending_machines ADD CONSTRAINT chk_next_service_after_created CHECK (next_service_date > created_date);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_products_price_positive') THEN
        ALTER TABLE products ADD CONSTRAINT chk_products_price_positive CHECK (price > 0);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_products_min_stock_non_negative') THEN
        ALTER TABLE products ADD CONSTRAINT chk_products_min_stock_non_negative CHECK (min_stock >= 0);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_products_sales_trend_non_negative') THEN
        ALTER TABLE products ADD CONSTRAINT chk_products_sales_trend_non_negative CHECK (sales_trend >= 0);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_machine_stock_non_negative') THEN
        ALTER TABLE machine_stock ADD CONSTRAINT chk_machine_stock_non_negative CHECK (quantity_available >= 0);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_sales_quantity_positive') THEN
        ALTER TABLE sales ADD CONSTRAINT chk_sales_quantity_positive CHECK (quantity > 0);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_sales_amount_positive') THEN
        ALTER TABLE sales ADD CONSTRAINT chk_sales_amount_positive CHECK (amount > 0);
    END IF;
END $$;

CREATE OR REPLACE FUNCTION trg_vending_machine_validate_and_fill()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM vending_machines
        WHERE serial_number = NEW.serial_number
          AND id <> COALESCE(NEW.id, '00000000-0000-0000-0000-000000000000'::UUID)
    ) THEN
        RAISE EXCEPTION 'ТА с таким серийным номером уже существует';
    END IF;

    IF EXISTS (
        SELECT 1 FROM vending_machines
        WHERE inventory_number = NEW.inventory_number
          AND id <> COALESCE(NEW.id, '00000000-0000-0000-0000-000000000000'::UUID)
    ) THEN
        RAISE EXCEPTION 'ТА с таким инвентарным номером уже существует';
    END IF;

    NEW.next_verification_date := (NEW.last_verification_date + (NEW.verification_interval_months || ' months')::INTERVAL)::DATE;
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tr_vending_machine_validate_and_fill ON vending_machines;
CREATE TRIGGER tr_vending_machine_validate_and_fill
BEFORE INSERT OR UPDATE ON vending_machines
FOR EACH ROW EXECUTE FUNCTION trg_vending_machine_validate_and_fill();

CREATE OR REPLACE FUNCTION trg_sales_update_machine_income()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE vending_machines
    SET total_income = total_income + NEW.amount,
        updated_at = NOW()
    WHERE id = NEW.machine_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tr_sales_update_machine_income ON sales;
CREATE TRIGGER tr_sales_update_machine_income
AFTER INSERT ON sales
FOR EACH ROW EXECUTE FUNCTION trg_sales_update_machine_income();

