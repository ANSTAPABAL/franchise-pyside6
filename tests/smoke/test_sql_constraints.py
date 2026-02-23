import os

import psycopg2
import pytest


def _db_params():
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": os.getenv("DB_NAME", "pyside6practice"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "root"),
    }


@pytest.mark.smoke
def test_unique_serial_number_constraint():
    conn = psycopg2.connect(**_db_params())
    conn.autocommit = False
    try:
        cur = conn.cursor()
        cur.execute("SELECT serial_number, inventory_number FROM vending_machines LIMIT 1")
        row = cur.fetchone()
        if not row:
            pytest.skip("Нет данных vending_machines для smoke проверки.")

        serial, inventory = row
        with pytest.raises(psycopg2.Error):
            cur.execute(
                """
                INSERT INTO vending_machines (
                    name, location, model, machine_type, total_income,
                    serial_number, inventory_number, manufacturer,
                    manufacture_date, commissioned_date, created_date,
                    last_verification_date, verification_interval_months,
                    resource_hours, next_service_date, service_duration_hours,
                    status, production_country, inventory_date
                ) VALUES (
                    'dup', 'loc', 'model', 'mixed', 0,
                    %s, %s || '-dup', 'maker',
                    CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE - INTERVAL '5 days', CURRENT_DATE,
                    CURRENT_DATE - INTERVAL '2 days', 12,
                    100, CURRENT_DATE + INTERVAL '1 day', 2,
                    'working', 'Россия', CURRENT_DATE
                )
                """,
                (serial, inventory),
            )
    finally:
        conn.rollback()
        conn.close()
