from __future__ import annotations

from core.db import db_cursor


def list_machines(search: str = '', limit: int = 20, offset: int = 0, company_folder_id: str | None = None):
    where = ['1=1']
    params: list = []

    if search:
        where.append('m.name ILIKE %s')
        params.append(f'%{search}%')
    if company_folder_id:
        where.append('m.company_id = %s')
        params.append(company_folder_id)

    where_sql = ' AND '.join(where)
    count_sql = f'SELECT COUNT(*) AS total FROM vending_machines m WHERE {where_sql}'
    data_sql = f'''
        SELECT
            m.id,
            m.name,
            m.serial_number,
            m.model,
            c.name AS company_name,
            md.modem_uid AS modem_uid,
            m.location,
            m.commissioned_date,
            m.status
        FROM vending_machines m
        LEFT JOIN companies c ON c.id = m.company_id
        LEFT JOIN modems md ON md.id = m.modem_id
        WHERE {where_sql}
        ORDER BY m.created_at DESC
        LIMIT %s OFFSET %s
    '''

    with db_cursor() as cur:
        cur.execute(count_sql, tuple(params))
        total = int(cur.fetchone()['total'])

        params2 = [*params, limit, offset]
        cur.execute(data_sql, tuple(params2))
        rows = cur.fetchall()

    return total, [dict(r) for r in rows]


def list_company_folders() -> list[dict]:
    with db_cursor() as cur:
        cur.execute('SELECT id, name FROM companies ORDER BY name')
        rows = cur.fetchall()
    return [dict(r) for r in rows]


def delete_machine(machine_id: str) -> None:
    with db_cursor(commit=True) as cur:
        cur.execute('DELETE FROM vending_machines WHERE id = %s', (machine_id,))


def unbind_modem(machine_id: str) -> None:
    with db_cursor(commit=True) as cur:
        cur.execute('UPDATE vending_machines SET modem_id = NULL, updated_at = NOW() WHERE id = %s', (machine_id,))


def upsert_machine(payload: dict) -> str:
    machine_id = payload.get('id')
    if machine_id:
        with db_cursor(commit=True) as cur:
            cur.execute(
                '''
                UPDATE vending_machines
                SET
                    name = %(name)s,
                    location = %(location)s,
                    model = %(model)s,
                    machine_type = %(machine_type)s,
                    total_income = %(total_income)s,
                    serial_number = %(serial_number)s,
                    inventory_number = %(inventory_number)s,
                    manufacturer = %(manufacturer)s,
                    manufacture_date = %(manufacture_date)s,
                    commissioned_date = %(commissioned_date)s,
                    last_verification_date = %(last_verification_date)s,
                    verification_interval_months = %(verification_interval_months)s,
                    resource_hours = %(resource_hours)s,
                    next_service_date = %(next_service_date)s,
                    service_duration_hours = %(service_duration_hours)s,
                    status = %(status)s,
                    production_country = %(production_country)s,
                    inventory_date = %(inventory_date)s,
                    last_verifier_user_id = %(last_verifier_user_id)s,
                    updated_at = NOW()
                WHERE id = %(id)s
                ''',
                payload,
            )
        return machine_id

    with db_cursor(commit=True) as cur:
        cur.execute(
            '''
            INSERT INTO vending_machines (
                name, location, model, machine_type, total_income,
                serial_number, inventory_number, manufacturer,
                manufacture_date, commissioned_date, last_verification_date,
                verification_interval_months, resource_hours, next_service_date,
                service_duration_hours, status, production_country,
                inventory_date, last_verifier_user_id, company_id
            ) VALUES (
                %(name)s, %(location)s, %(model)s, %(machine_type)s, %(total_income)s,
                %(serial_number)s, %(inventory_number)s, %(manufacturer)s,
                %(manufacture_date)s, %(commissioned_date)s, %(last_verification_date)s,
                %(verification_interval_months)s, %(resource_hours)s, %(next_service_date)s,
                %(service_duration_hours)s, %(status)s, %(production_country)s,
                %(inventory_date)s, %(last_verifier_user_id)s, %(company_id)s
            )
            RETURNING id
            ''',
            payload,
        )
        row = cur.fetchone()
    return str(row['id'])
