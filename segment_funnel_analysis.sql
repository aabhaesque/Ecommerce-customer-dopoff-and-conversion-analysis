-- ============================================================
-- E-COMMERCE SEGMENT-LEVEL FUNNEL ANALYSIS
-- Session-level comparison across device, traffic and region
-- ============================================================


WITH session_funnel AS (

    SELECT

        session_id,

        device_type,

        traffic_source,

        region,

        MAX(
            CASE
                WHEN event_type = 'product_view'
                THEN 1 ELSE 0
            END
        ) AS viewed_product,

        MAX(
            CASE
                WHEN event_type = 'add_to_cart'
                THEN 1 ELSE 0
            END
        ) AS added_to_cart,

        MAX(
            CASE
                WHEN event_type = 'checkout_start'
                THEN 1 ELSE 0
            END
        ) AS started_checkout,

        MAX(
            CASE
                WHEN event_type = 'purchase'
                THEN 1 ELSE 0
            END
        ) AS purchased

    FROM ecommerce_user_events

    GROUP BY
        session_id,
        device_type,
        traffic_source,
        region
)


-- ============================================================
-- DEVICE SEGMENT
-- ============================================================

SELECT

    'device_type' AS segment_type,

    device_type AS segment_value,

    COUNT(*) AS sessions,

    SUM(viewed_product) AS product_views,

    SUM(added_to_cart) AS add_to_carts,

    SUM(started_checkout) AS checkout_starts,

    SUM(purchased) AS purchases,

    ROUND(
        100.0 * SUM(added_to_cart) /
        NULLIF(SUM(viewed_product), 0),
        2
    ) AS view_to_cart_rate,

    ROUND(
        100.0 * SUM(started_checkout) /
        NULLIF(SUM(added_to_cart), 0),
        2
    ) AS cart_to_checkout_rate,

    ROUND(
        100.0 * SUM(purchased) /
        NULLIF(SUM(started_checkout), 0),
        2
    ) AS checkout_to_purchase_rate,

    ROUND(
        100.0 * SUM(purchased) /
        NULLIF(SUM(viewed_product), 0),
        2
    ) AS overall_purchase_rate

FROM session_funnel

GROUP BY device_type


UNION ALL


-- ============================================================
-- TRAFFIC SOURCE SEGMENT
-- ============================================================

SELECT

    'traffic_source' AS segment_type,

    traffic_source AS segment_value,

    COUNT(*) AS sessions,

    SUM(viewed_product) AS product_views,

    SUM(added_to_cart) AS add_to_carts,

    SUM(started_checkout) AS checkout_starts,

    SUM(purchased) AS purchases,

    ROUND(
        100.0 * SUM(added_to_cart) /
        NULLIF(SUM(viewed_product), 0),
        2
    ) AS view_to_cart_rate,

    ROUND(
        100.0 * SUM(started_checkout) /
        NULLIF(SUM(added_to_cart), 0),
        2
    ) AS cart_to_checkout_rate,

    ROUND(
        100.0 * SUM(purchased) /
        NULLIF(SUM(started_checkout), 0),
        2
    ) AS checkout_to_purchase_rate,

    ROUND(
        100.0 * SUM(purchased) /
        NULLIF(SUM(viewed_product), 0),
        2
    ) AS overall_purchase_rate

FROM session_funnel

GROUP BY traffic_source


UNION ALL


-- ============================================================
-- REGION SEGMENT
-- ============================================================

SELECT

    'region' AS segment_type,

    region AS segment_value,

    COUNT(*) AS sessions,

    SUM(viewed_product) AS product_views,

    SUM(added_to_cart) AS add_to_carts,

    SUM(started_checkout) AS checkout_starts,

    SUM(purchased) AS purchases,

    ROUND(
        100.0 * SUM(added_to_cart) /
        NULLIF(SUM(viewed_product), 0),
        2
    ) AS view_to_cart_rate,

    ROUND(
        100.0 * SUM(started_checkout) /
        NULLIF(SUM(added_to_cart), 0),
        2
    ) AS cart_to_checkout_rate,

    ROUND(
        100.0 * SUM(purchased) /
        NULLIF(SUM(started_checkout), 0),
        2
    ) AS checkout_to_purchase_rate,

    ROUND(
        100.0 * SUM(purchased) /
        NULLIF(SUM(viewed_product), 0),
        2
    ) AS overall_purchase_rate

FROM session_funnel

GROUP BY region;