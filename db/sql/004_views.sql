CREATE OR REPLACE VIEW vw_network_efficiency AS
SELECT
    COALESCE(
        ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'working') / NULLIF(COUNT(*), 0), 2),
        0
    ) AS working_percent
FROM vending_machines;

CREATE OR REPLACE VIEW vw_status_breakdown AS
SELECT status, COUNT(*) AS cnt
FROM vending_machines
GROUP BY status;

CREATE OR REPLACE VIEW vw_summary AS
SELECT
    COALESCE(SUM(amount), 0) AS sales_total,
    COALESCE((SELECT SUM(cash_amount) FROM machine_monitor_snapshot), 0) AS cash_total,
    COALESCE((SELECT COUNT(*) FROM maintenance_records), 0) AS maintenance_count
FROM sales;

CREATE OR REPLACE VIEW vw_sales_last_10_days_amount AS
WITH days AS (
    SELECT generate_series(CURRENT_DATE - INTERVAL '9 days', CURRENT_DATE, INTERVAL '1 day')::DATE AS day
)
SELECT d.day, COALESCE(SUM(s.amount), 0)::NUMERIC(12,2) AS value
FROM days d
LEFT JOIN sales s ON s.sold_at::DATE = d.day
GROUP BY d.day;

CREATE OR REPLACE VIEW vw_sales_last_10_days_quantity AS
WITH days AS (
    SELECT generate_series(CURRENT_DATE - INTERVAL '9 days', CURRENT_DATE, INTERVAL '1 day')::DATE AS day
)
SELECT d.day, COALESCE(SUM(s.quantity), 0)::NUMERIC(12,2) AS value
FROM days d
LEFT JOIN sales s ON s.sold_at::DATE = d.day
GROUP BY d.day;
