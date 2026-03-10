"""сервис данных для страницы «монитор та».

строит sql-запрос с фильтрами и возвращает:
  - строки таблицы (один dict на каждый автомат);
  - итоги по отфильтрованному набору (количество + сумма денег).
"""

from __future__ import annotations

from core.db import db_cursor


def monitor_rows(
    state: str | None,
    connection_type: str | None,
    extra_status: str | None,
):
    """возвращает (rows, totals) для страницы мониторинга.

    как работает:
    - фильтры строятся динамически: WHERE 1=1 AND ... — классический приём,
      чтобы добавлять условия через AND без проверки «а первое ли оно»;
    - COALESCE(md.connection_type, %s) = %s — работает даже если у автомата
      нет модема, connection_type тогда будет NULL;
    - ROW_NUMBER() OVER (ORDER BY m.name) — нумерация строк прямо в sql,
      python её не считает сам;
    - machine_monitor_snapshot — таблица со снапшотами: загрузка, деньги,
      события, статус оборудования.

    возвращает:
        rows   — list[dict]: num, tp, connection, load, cash, events,
                 equipment, info, extra, id
        totals — {'machines': int, 'money': float}
    """
    # динамически собираем условия WHERE
    where = ['1=1']
    params = []

    if state:
        where.append('m.status = %s')
        params.append(state)
    if connection_type:
        # coalesce нужен, чтобы фильтр сработал даже при NULL в modems
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
            COALESCE(NULLIF(TRIM(md.provider), ''), '—') AS connection,
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

    # итоги считаем на python по уже отфильтрованным строкам
    totals = {
        'machines': len(rows),
        'money': sum(float(r['cash']) for r in rows),
    }
    return rows, totals
