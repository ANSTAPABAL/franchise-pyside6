from __future__ import annotations

from core.db import db_cursor


def monitor_rows(state: str | None, connection_type: str | None, extra_status: str | None):
    where = ['1=1']
    params = []

    if state:
        where.append('m.status = %s')
        params.append(state)
    if connection_type:
        where.append('COALESCE(md.connection_type, %s) = %s')
        params.append(connection_type)
        params.append(connection_type)
    if extra_status:
        where.append('COALESCE(m.extra_status, %s) = %s')
        params.append(extra_status)
        params.append(extra_status)

    sql = f'''
        SELECT
            ROW_NUMBER() OVER (ORDER BY m.name) AS num,
            m.name AS tp,
            COALESCE(md.provider, 'N/A') AS connection,
            ROUND(COALESCE(ms.load_percent, 0)::numeric, 2) AS load,
            ROUND(COALESCE(ms.cash_amount, 0)::numeric, 2) AS cash,
            COALESCE(ms.events, 'Нет событий') AS events,
            COALESCE(ms.equipment_status, 'green') AS equipment,
            m.location AS info,
            COALESCE(m.extra_status, '-') AS extra,
            m.id
        FROM vending_machines m
        LEFT JOIN modems md ON md.id = m.modem_id
        LEFT JOIN machine_monitor_snapshot ms ON ms.machine_id = m.id
        WHERE {' AND '.join(where)}
        ORDER BY m.name
    '''

    with db_cursor() as cur:
        cur.execute(sql, tuple(params))
        rows = [dict(r) for r in cur.fetchall()]

    totals = {
        'machines': len(rows),
        'money': sum(float(r['cash']) for r in rows),
    }
    return rows, totals
