"""сервис данных для главной страницы (dashboard).

dashboard_page берёт данные отсюда — агрегаты и серии для графиков.

фишка архитектуры: все тяжёлые подсчёты вынесены в postgresql-представления (vw_*),
python только читает готовый результат — так быстрее и проще.
"""

from __future__ import annotations

from core.db import db_cursor


def network_efficiency() -> float:
    """процент работающих автоматов из представления vw_network_efficiency.

    если представление вернуло пустоту — возвращаем 0.0, не падаем с ошибкой.
    """
    with db_cursor() as cur:
        cur.execute('SELECT * FROM vw_network_efficiency')
        row = cur.fetchone()
    return float(row['working_percent']) if row else 0.0


def network_status_breakdown() -> dict:
    """количество автоматов в каждом статусе: working / broken / maintenance.

    результат идёт в круговую диаграмму (QPieSeries) на главной странице.
    пример: {'working': 42, 'broken': 3, 'maintenance': 5}
    """
    with db_cursor() as cur:
        cur.execute('SELECT status, cnt FROM vw_status_breakdown ORDER BY status')
        rows = cur.fetchall()
    # cnt в бд хранится как numeric, явно приводим к int
    return {r['status']: int(r['cnt']) for r in rows}


def summary_cards() -> dict:
    """сводные цифры: сумма продаж, деньги в автоматах, количество обслуживаний.

    читает одну строку из vw_summary.
    возвращает dict с ключами: sales_total, cash_total, maintenance_count.
    """
    with db_cursor() as cur:
        cur.execute('SELECT * FROM vw_summary')
        row = cur.fetchone()
    return {
        'sales_total': float(row['sales_total']) if row else 0.0,
        'cash_total': float(row['cash_total']) if row else 0.0,
        'maintenance_count': int(row['maintenance_count']) if row else 0,
    }


def sales_last_10_days(metric: str = 'amount') -> list[tuple[str, float]]:
    """данные для столбчатого графика за последние 10 дней.

    metric='amount'   — по сумме продаж в рублях;
    metric='quantity' — по количеству проданных единиц.

    фишка: имя представления строится динамически:
        vw_sales_last_10_days_amount  или  vw_sales_last_10_days_quantity.
    возвращает список кортежей [(дата_строка, значение), ...].
    """
    col = 'amount' if metric == 'amount' else 'quantity'
    with db_cursor() as cur:
        cur.execute(
            f'''
            SELECT to_char(day, 'YYYY-MM-DD') AS day, value
            FROM vw_sales_last_10_days_{col}
            ORDER BY day
            '''
        )
        rows = cur.fetchall()
    return [(r['day'], float(r['value'])) for r in rows]


def franchise_news(limit: int = 10) -> list[dict]:
    """последние новости для блока «новости» на главной.

    возвращает список dict с ключами: id, title, body, created_at.
    limit — сколько записей взять (по умолчанию 10).
    """
    with db_cursor() as cur:
        cur.execute(
            '''
            SELECT id, title, body, created_at
            FROM news
            ORDER BY created_at DESC
            LIMIT %s
            ''',
            (limit,),
        )
        rows = cur.fetchall()
    return [dict(r) for r in rows]
