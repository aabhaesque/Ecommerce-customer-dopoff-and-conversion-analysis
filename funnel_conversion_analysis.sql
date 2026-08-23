-- ============================================================
-- E-COMMERCE FUNNEL CONVERSION ANALYSIS
-- Session-level funnel analysis
-- ============================================================

WITH session_funnel AS (

    SELECT
        session_id,

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

    GROUP BY session_id
),

funnel_counts AS (

    SELECT
        SUM(viewed_product) AS product_views,
        SUM(added_to_cart) AS add_to_carts,
        SUM(started_checkout) AS checkout_starts,
        SUM(purchased) AS purchases

    FROM session_funnel
)

SELECT

    product_views,

    add_to_carts,

    checkout_starts,

    purchases,

    ROUND(
        100.0 * add_to_carts /
        NULLIF(product_views, 0),
        2
    ) AS view_to_cart_rate,

    ROUND(
        100.0 * checkout_starts /
        NULLIF(add_to_carts, 0),
        2
    ) AS cart_to_checkout_rate,

    ROUND(
        100.0 * purchases /
        NULLIF(checkout_starts, 0),
        2
    ) AS checkout_to_purchase_rate,

    ROUND(
        100.0 * purchases /
        NULLIF(product_views, 0),
        2
    ) AS overall_purchase_rate

FROM funnel_counts;