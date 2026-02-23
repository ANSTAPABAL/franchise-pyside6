from __future__ import annotations

from core.db import db_cursor


def network_efficiency() -> float:
    with db_cursor() as cur:
        cur.execute('SELECT * FROM vw_network_efficiency')
        row = cur.fetchone()
    return float(row['working_percent']) if row else 0.0


def network_status_breakdown() -> dict:
    with db_cursor() as cur:
        cur.execute('SELECT status, cnt FROM vw_status_breakdown ORDER BY status')
        rows = cur.fetchall()
    return {r['status']: int(r['cnt']) for r in rows}


def summary_cards() -> dict:
    with db_cursor() as cur:
        cur.execute('SELECT * FROM vw_summary')
        row = cur.fetchone()
    return {
        'sales_total': float(row['sales_total']) if row else 0.0,
        'cash_total': float(row['cash_total']) if row else 0.0,
        'maintenance_count': int(row['maintenance_count']) if row else 0,
    }


def sales_last_10_days(metric: str = 'amount') -> list[tuple[str, float]]:
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
