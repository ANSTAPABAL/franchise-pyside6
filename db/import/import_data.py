from __future__ import annotations

import csv
import json
import re
from datetime import datetime
from pathlib import Path

import openpyxl

from core.db import db_cursor
from core.settings import settings

UUID_RE = re.compile(r"^[0-9a-fA-F-]{36}$")


def find_import_dir(root_hint: str) -> Path:
    root = Path(root_hint) if root_hint else Path.cwd()
    for path in root.rglob("*"):
        if path.is_dir() and path.name.lower() == "import":
            return path
    raise FileNotFoundError("Не найдена папка Import. Проверьте IMPORT_ROOT в .env.")


def parse_dt(value: str):
    value = (value or "").strip()
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def ensure_company(name: str) -> str | None:
    if not name:
        return None
    with db_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO companies(name) VALUES (%s)
            ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
            RETURNING id
            """,
            (name,),
        )
        row = cur.fetchone()
    return str(row["id"]) if row else None


def ensure_payment_method(name: str) -> int:
    lowered = (name or "").lower()
    if "карт" in lowered:
        code, title = "card", "Карта"
    elif "qr" in lowered:
        code, title = "qr", "QR"
    else:
        code, title = "cash", "Наличные"
    with db_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO payment_methods(code, name) VALUES (%s, %s)
            ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name
            RETURNING id
            """,
            (code, title),
        )
        row = cur.fetchone()
    return int(row["id"])


def import_users(import_dir: Path):
    users_dir = import_dir / "users"
    if not users_dir.exists():
        return
    for file in users_dir.glob("*.json"):
        data = json.loads(file.read_text(encoding="utf-8-sig"))
        role = "admin" if data.get("is_manager") else "operator"
        with db_cursor(commit=True) as cur:
            cur.execute(
                """
                INSERT INTO users (id, full_name, email, phone, role, password_hash, is_active, password_plain)
                VALUES (%s, %s, %s, %s, %s, %s, TRUE, %s)
                ON CONFLICT (id) DO UPDATE SET
                    full_name = EXCLUDED.full_name,
                    email = EXCLUDED.email,
                    phone = EXCLUDED.phone,
                    role = EXCLUDED.role,
                    password_hash = EXCLUDED.password_hash,
                    password_plain = EXCLUDED.password_plain
                """,
                (
                    data["id"],
                    data.get("full_name") or "Без ФИО",
                    data.get("email") or f"{data['id']}@local",
                    data.get("phone"),
                    role,
                    "123",
                    "123",
                ),
            )
            cur.execute(
                """
                INSERT INTO user_profiles (user_id, photo_base64)
                VALUES (%s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                    photo_base64 = EXCLUDED.photo_base64,
                    updated_at = NOW()
                """,
                (data["id"], data.get("image")),
            )


def import_vending_machines(import_dir: Path):
    path = import_dir / "vending_machines.csv"
    if not path.exists():
        return
    rows = path.read_text(encoding="cp1251").splitlines()
    if len(rows) <= 1:
        return

    for raw in rows[1:]:
        if not raw.strip():
            continue
        parts = raw.split(";")
        uuids = [p.strip() for p in parts if UUID_RE.match(p.strip())]
        # В строках обычно два UUID: user_id и machine_id. Нужен machine_id.
        machine_id = uuids[1] if len(uuids) > 1 else (uuids[0] if uuids else None)
        if not machine_id:
            continue
        serial = parts[0].strip()
        name = parts[1].strip() or serial
        company_name = next((p.strip() for p in parts if p.strip().startswith("ООО")), "ООО Импорт")
        company_id = ensure_company(company_name)
        status_src = raw.lower()
        status = "maintenance" if "обслуж" in status_src else ("broken" if "не работ" in status_src else "working")
        dt_part = next((p for p in parts if p.strip().startswith("20")), "")
        install_dt = parse_dt(dt_part) or datetime.now()
        base_date = install_dt.date()

        with db_cursor(commit=True) as cur:
            cur.execute(
                """
                INSERT INTO vending_machines (
                    id, company_id, name, location, model, machine_type, total_income,
                    serial_number, inventory_number, manufacturer, manufacture_date,
                    commissioned_date, created_date, last_verification_date,
                    verification_interval_months, resource_hours, next_service_date,
                    service_duration_hours, status, production_country, inventory_date
                ) VALUES (
                    %s, %s, %s, %s, %s, 'mixed', 0,
                    %s, %s, 'Unknown', %s, %s, CURRENT_DATE, CURRENT_DATE,
                    12, 10000, CURRENT_DATE + INTERVAL '10 days', 4, %s, 'Россия', CURRENT_DATE
                )
                ON CONFLICT (serial_number) DO UPDATE SET
                    id = EXCLUDED.id,
                    company_id = EXCLUDED.company_id,
                    name = EXCLUDED.name,
                    status = EXCLUDED.status,
                    updated_at = NOW()
                """,
                (
                    machine_id,
                    company_id,
                    name,
                    "Импортированная локация",
                    "Unknown",
                    serial,
                    f"INV-{serial}",
                    base_date,
                    base_date,
                    status,
                ),
            )


def import_products(import_dir: Path):
    path = import_dir / "products.json"
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    for item in data:
        with db_cursor(commit=True) as cur:
            cur.execute(
                """
                INSERT INTO products (id, name, description, price, min_stock, sales_trend)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    price = EXCLUDED.price,
                    min_stock = EXCLUDED.min_stock,
                    sales_trend = EXCLUDED.sales_trend
                """,
                (
                    item["id"],
                    item.get("name"),
                    item.get("description"),
                    float(item.get("price") or 0),
                    int(item.get("min_stock") or 0),
                    float(item.get("sales_trend") or 0),
                ),
            )
            machine_id = item.get("vending_machine_id")
            if machine_id and UUID_RE.match(machine_id):
                cur.execute("SELECT 1 FROM vending_machines WHERE id = %s", (machine_id,))
                if cur.fetchone():
                    cur.execute(
                        """
                        INSERT INTO machine_stock (machine_id, product_id, quantity_available)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (machine_id, product_id) DO UPDATE SET quantity_available = EXCLUDED.quantity_available
                        """,
                        (machine_id, item["id"], int(item.get("quantity_available") or 0)),
                    )


def import_sales(import_dir: Path):
    path = import_dir / "sales.csv"
    if not path.exists():
        return
    with path.open("r", encoding="cp1251", newline="") as file:
        reader = csv.DictReader(file, delimiter=";")
        for row in reader:
            sold_at = parse_dt(row.get("timestamp", ""))
            if not sold_at:
                continue
            product_id = row.get("product_id")
            with db_cursor() as cur:
                cur.execute(
                    """
                    SELECT machine_id
                    FROM machine_stock
                    WHERE product_id = %s
                    ORDER BY quantity_available DESC
                    LIMIT 1
                    """,
                    (product_id,),
                )
                machine = cur.fetchone()
            if not machine:
                continue
            method_id = ensure_payment_method(row.get("payment_method"))
            with db_cursor(commit=True) as cur:
                cur.execute(
                    """
                    INSERT INTO sales (machine_id, product_id, quantity, amount, sold_at, payment_method_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        machine["machine_id"],
                        product_id,
                        int(row.get("quantity") or 0),
                        float(row.get("total_price") or 0),
                        sold_at,
                        method_id,
                    ),
                )


def import_maintenance(import_dir: Path):
    xlsx = import_dir / "maintenance.xlsx"
    if not xlsx.exists():
        return
    wb = openpyxl.load_workbook(xlsx, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return
    header = [str(c).strip().lower() if c is not None else "" for c in rows[0]]
    data_rows = rows[1:]

    def col_idx(*variants: str) -> int | None:
        for v in variants:
            if v in header:
                return header.index(v)
        return None

    i_machine = col_idx("vending_machine_id", "machine_id", "id автомата", "id_автомата")
    i_date = col_idx("date", "maintenance_date", "дата обслуживания")
    i_desc = col_idx("work_description", "description", "описание", "описание работы")
    i_issues = col_idx("issues_found", "issues", "проблемы")
    i_exec = col_idx("executor_user_id", "исполнитель", "user_id")

    with db_cursor(commit=True) as cur:
        for row in data_rows:
            if not row:
                continue
            machine_id = str(row[i_machine]).strip() if i_machine is not None and row[i_machine] else None
            if not machine_id or not UUID_RE.match(machine_id):
                continue
            cur.execute("SELECT 1 FROM vending_machines WHERE id = %s", (machine_id,))
            if not cur.fetchone():
                continue
            date_raw = str(row[i_date]).strip() if i_date is not None and row[i_date] else ""
            date_val = parse_dt(date_raw)
            if not date_val:
                continue
            desc = str(row[i_desc]).strip() if i_desc is not None and row[i_desc] else "Обслуживание"
            issues = str(row[i_issues]).strip() if i_issues is not None and row[i_issues] else None
            exec_user = str(row[i_exec]).strip() if i_exec is not None and row[i_exec] else None
            exec_user = exec_user if exec_user and UUID_RE.match(exec_user) else None
            cur.execute(
                """
                INSERT INTO maintenance_records (machine_id, maintenance_date, work_description, issues, executor_user_id)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (machine_id, date_val.date(), desc, issues, exec_user),
            )


def populate_monitor_snapshots():
    with db_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO machine_monitor_snapshot (machine_id, load_percent, cash_amount, events, equipment_status)
            SELECT vm.id,
                   (50 + (abs(('x' || substr(md5(vm.id::text), 1, 8))::bit(32)::int) % 50))::numeric(5,2),
                   (1000 + (abs(('x' || substr(md5(vm.serial_number), 1, 8))::bit(32)::int) % 20000))::numeric(12,2),
                   'Нет критических событий',
                   CASE vm.status WHEN 'working' THEN 'green' WHEN 'broken' THEN 'red' ELSE 'blue' END
            FROM vending_machines vm
            ON CONFLICT (machine_id) DO UPDATE SET
                load_percent = EXCLUDED.load_percent,
                cash_amount = EXCLUDED.cash_amount,
                events = EXCLUDED.events,
                equipment_status = EXCLUDED.equipment_status,
                updated_at = NOW()
            """
        )


def main():
    import_dir = find_import_dir(settings.import_root)
    print(f"Import dir: {import_dir}")
    import_users(import_dir)
    import_vending_machines(import_dir)
    import_products(import_dir)
    import_sales(import_dir)
    import_maintenance(import_dir)
    populate_monitor_snapshots()
    print("Import done")


if __name__ == "__main__":
    main()
