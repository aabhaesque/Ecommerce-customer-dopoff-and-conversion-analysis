import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv("data/ecommerce_user_events.csv")

df["event_time"] = pd.to_datetime(df["event_time"])

df = df.sort_values(
    ["session_id", "event_time"]
).reset_index(drop=True)


# ============================================================
# CREATE SESSION-LEVEL DATA FOR BUSINESS ANALYSIS
# ============================================================

session_df = df.groupby("session_id").agg(
    user_id=("user_id", "first"),
    device_type=("device_type", "first"),
    traffic_source=("traffic_source", "first"),
    region=("region", "first"),
    unique_categories=("product_category", "nunique"),
    total_events=("event_type", "count"),
    session_start=("event_time", "min"),
    session_end=("event_time", "max")
).reset_index()

session_df["session_duration_min"] = (
    session_df["session_end"]
    - session_df["session_start"]
).dt.total_seconds() / 60


# ============================================================
# CREATE CONVERSION TARGET
# ============================================================

purchase_sessions = (
    df.groupby("session_id")["event_type"]
    .apply(lambda x: int("purchase" in x.values))
    .rename("converted")
)

session_df = session_df.merge(
    purchase_sessions,
    on="session_id",
    how="left"
)


# ============================================================
# 1. FUNNEL CONVERSION
# ============================================================

event_counts = df["event_type"].value_counts()

funnel_order = [
    "product_view",
    "add_to_cart",
    "checkout_start",
    "purchase"
]

funnel_counts = [
    event_counts.get(event, 0)
    for event in funnel_order
]

funnel_labels = [
    "Product View",
    "Add to Cart",
    "Checkout",
    "Purchase"
]

plt.figure(figsize=(9, 5))

bars = plt.bar(
    funnel_labels,
    funnel_counts
)

plt.title("E-commerce Conversion Funnel")
plt.ylabel("Number of Events")
plt.xlabel("Funnel Stage")

for bar, value in zip(bars, funnel_counts):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        str(value),
        ha="center",
        va="bottom"
    )

plt.tight_layout()

plt.savefig(
    "outputs/conversion_funnel.png",
    dpi=300
)

plt.close()


# ============================================================
# 2. CONVERSION BY DEVICE
# ============================================================

device_conversion = (
    session_df
    .groupby("device_type")["converted"]
    .mean()
    .sort_values(ascending=False)
)

plt.figure(figsize=(8, 5))

bars = plt.bar(
    device_conversion.index,
    device_conversion.values
)

plt.title("Conversion Rate by Device")
plt.ylabel("Conversion Rate")
plt.xlabel("Device Type")

plt.ylim(0, max(device_conversion.values) * 1.25)

for bar, value in zip(
    bars,
    device_conversion.values
):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        value,
        f"{value:.1%}",
        ha="center",
        va="bottom"
    )

plt.tight_layout()

plt.savefig(
    "outputs/conversion_by_device.png",
    dpi=300
)

plt.close()


# ============================================================
# 3. CONVERSION BY TRAFFIC SOURCE
# ============================================================

traffic_conversion = (
    session_df
    .groupby("traffic_source")["converted"]
    .mean()
    .sort_values(ascending=False)
)

plt.figure(figsize=(9, 5))

bars = plt.bar(
    traffic_conversion.index,
    traffic_conversion.values
)

plt.title("Conversion Rate by Traffic Source")
plt.ylabel("Conversion Rate")
plt.xlabel("Traffic Source")

plt.xticks(rotation=30)

plt.ylim(0, max(traffic_conversion.values) * 1.25)

for bar, value in zip(
    bars,
    traffic_conversion.values
):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        value,
        f"{value:.1%}",
        ha="center",
        va="bottom"
    )

plt.tight_layout()

plt.savefig(
    "outputs/conversion_by_traffic_source.png",
    dpi=300
)

plt.close()


# ============================================================
# 4. CREATE EARLY-SESSION BEHAVIOUR
# ============================================================

def create_early_features(group):

    group = group.sort_values("event_time")

    n_events = len(group)

    early_n = max(
        1,
        int(np.ceil(n_events * 0.5))
    )

    early = group.iloc[:early_n]

    early_duration = (
        early["event_time"].max()
        - early["event_time"].min()
    ).total_seconds() / 60

    return pd.Series({
        "early_events": len(early),
        "early_duration_min": early_duration,
        "event_type_diversity": early["event_type"].nunique()
    })


early_features = (
    df.groupby("session_id")
    .apply(
        create_early_features,
        include_groups=False
    )
    .reset_index()
)

early_features = early_features.merge(
    purchase_sessions,
    on="session_id",
    how="left"
)


# ============================================================
# 5. EARLY ENGAGEMENT BY CONVERSION
# ============================================================

engagement = (
    early_features
    .groupby("converted")[
        [
            "early_events",
            "early_duration_min",
            "event_type_diversity"
        ]
    ]
    .mean()
)

engagement.index = [
    "Non-Converted",
    "Converted"
]

engagement.plot(
    kind="bar",
    figsize=(9, 5)
)

plt.title(
    "Early Session Engagement by Conversion"
)

plt.ylabel("Average Value")
plt.xlabel("Conversion Status")

plt.xticks(rotation=0)

plt.legend(
    title="Metric"
)

plt.tight_layout()

plt.savefig(
    "outputs/early_engagement.png",
    dpi=300
)

plt.close()


# ============================================================
# COMPLETE
# ============================================================

print("\nVisualization files created successfully:")

print(
    "- outputs/conversion_funnel.png"
)

print(
    "- outputs/conversion_by_device.png"
)

print(
    "- outputs/conversion_by_traffic_source.png"
)

print(
    "- outputs/early_engagement.png"
)