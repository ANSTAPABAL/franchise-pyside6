from __future__ import annotations

from core.db import db_cursor


def sales_report(limit: int = 200) -> list[dict]:
    with db_cursor() as cur:
        cur.execute(
            '''
            SELECT s.id, s.sold_at, s.amount, s.quantity,
                   p.name AS product_name,
                   m.name AS machine_name,
                   pm.name AS payment_method
            FROM sales s
            JOIN products p ON p.id = s.product_id
            JOIN vending_machines m ON m.id = s.machine_id
            JOIN payment_methods pm ON pm.id = s.payment_method_id
            ORDER BY s.sold_at DESC
            LIMIT %s
            ''',
            (limit,),
        )
        return [dict(r) for r in cur.fetchall()]


def stock_report(limit: int = 300) -> list[dict]:
    with db_cursor() as cur:
        cur.execute(
            '''
            SELECT ms.machine_id, m.name AS machine_name, ms.product_id, p.name AS product_name,
                   ms.quantity_available, p.min_stock,
                   CASE WHEN ms.quantity_available <= p.min_stock THEN TRUE ELSE FALSE END AS need_refill
            FROM machine_stock ms
            JOIN vending_machines m ON m.id = ms.machine_id
            JOIN products p ON p.id = ms.product_id
            ORDER BY m.name, p.name
            LIMIT %s
            ''',
            (limit,),
        )
        return [dict(r) for r in cur.fetchall()]
