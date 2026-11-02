
-- ============================================================
-- PROJECT: Temporal E-Commerce Order History
-- FILE: functions_and_testing.sql
-- PURPOSE:
-- 1. Find an order's status at a specific historical time.
-- 2. Calculate the time taken to deliver an order.
-- 3. Test the functions and verify the dataset.
-- ============================================================


-- ============================================================
-- FUNCTION 1: GET ORDER STATUS AT A HISTORICAL TIME
-- ============================================================

CREATE OR REPLACE FUNCTION get_order_status_at(
    p_order_id INTEGER,
    p_as_of TIMESTAMP
)
RETURNS TABLE (
    requested_order_id INTEGER,
    checked_at TIMESTAMP,
    status_at_time VARCHAR(20)
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Check whether the requested order exists.
    IF NOT EXISTS (
        SELECT 1
        FROM orders o
        WHERE o.order_id = p_order_id
    ) THEN
        RAISE EXCEPTION 'Order ID % does not exist', p_order_id;
    END IF;

    -- Find the status valid at the requested timestamp.
    RETURN QUERY
    SELECT
        h.order_id,
        p_as_of,
        h.status::VARCHAR(20)
    FROM order_status_history h
    WHERE h.order_id = p_order_id
      AND h.valid_from <= p_as_of
      AND (
          h.valid_until IS NULL
          OR p_as_of < h.valid_until
      )
    ORDER BY h.valid_from DESC
    LIMIT 1;
END;
$$;


-- ============================================================
-- FUNCTION 2: CALCULATE ORDER DELIVERY DURATION
-- ============================================================

CREATE OR REPLACE FUNCTION get_order_delivery_duration(
    p_order_id INTEGER
)
RETURNS TABLE (
    requested_order_id INTEGER,
    placed_at TIMESTAMP,
    delivered_at TIMESTAMP,
    hours_to_deliver NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_placed_at TIMESTAMP;
    v_delivered_at TIMESTAMP;
BEGIN
    -- Check whether the requested order exists.
    IF NOT EXISTS (
        SELECT 1
        FROM orders o
        WHERE o.order_id = p_order_id
    ) THEN
        RAISE EXCEPTION 'Order ID % does not exist', p_order_id;
    END IF;

    -- Find when the order was first marked PENDING.
    SELECT MIN(h.valid_from)
    INTO v_placed_at
    FROM order_status_history h
    WHERE h.order_id = p_order_id
      AND h.status = 'PENDING';

    -- Find when the order was first marked DELIVERED.
    SELECT MIN(h.valid_from)
    INTO v_delivered_at
    FROM order_status_history h
    WHERE h.order_id = p_order_id
      AND h.status = 'DELIVERED';

    -- Return the timestamps and delivery duration.
    RETURN QUERY
    SELECT
        p_order_id,
        v_placed_at,
        v_delivered_at,
        CASE
            WHEN v_placed_at IS NOT NULL
             AND v_delivered_at IS NOT NULL
             AND v_delivered_at >= v_placed_at
            THEN ROUND(
                (
                    EXTRACT(
                        EPOCH FROM (v_delivered_at - v_placed_at)
                    ) / 3600
                )::NUMERIC,
                2
            )
            ELSE NULL::NUMERIC
        END;
END;
$$;


-- ============================================================
-- TEST 1: VIEW THE COMPLETE HISTORY OF ORDER 1
-- ============================================================

SELECT
    order_id,
    status,
    valid_from,
    valid_until,
    notes
FROM order_status_history
WHERE order_id = 1
ORDER BY valid_from;


-- ============================================================
-- TEST 2: FIND ORDER 1'S STATUS AT A HISTORICAL TIME
-- ============================================================

SELECT *
FROM get_order_status_at(
    1,
    TIMESTAMP '2024-01-02 13:00:00'
);


-- ============================================================
-- TEST 3: CALCULATE ORDER 1'S DELIVERY DURATION
-- ============================================================

SELECT *
FROM get_order_delivery_duration(3);


-- ============================================================
-- TEST 4: VERIFY RECORD COUNTS
-- ============================================================

SELECT
    'customers' AS table_name,
    COUNT(*) AS total_records
FROM customers

UNION ALL

SELECT
    'orders',
    COUNT(*)
FROM orders

UNION ALL

SELECT
    'order_status_history',
    COUNT(*)
FROM order_status_history;


-- ============================================================
-- TEST 5: COUNT ORDERS BY THEIR CURRENT STATUS
-- ============================================================

SELECT
    current_status,
    COUNT(*) AS total_orders
FROM orders
GROUP BY current_status
ORDER BY current_status;


-- ============================================================
-- TEST 6: CHECK CURRENT STATUS AGAINST LATEST HISTORY
-- Ideally, this query should return zero rows.
-- ============================================================

SELECT
    o.order_id,
    o.current_status,
    h.status AS latest_history_status
FROM orders o
JOIN LATERAL (
    SELECT history.status
    FROM order_status_history history
    WHERE history.order_id = o.order_id
    ORDER BY
        history.valid_from DESC,
        history.history_id DESC
    LIMIT 1
) h ON TRUE
WHERE o.current_status <> h.status;
