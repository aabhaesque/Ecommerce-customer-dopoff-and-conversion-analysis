import numpy as np
import pandas as pd
from datetime import datetime, timedelta


# ============================================================
# CONFIGURATION
# ============================================================

np.random.seed(42)

N_SESSIONS = 6000

OUTPUT_FILE = "data/ecommerce_user_events.csv"


# ============================================================
# CUSTOMER / SESSION ATTRIBUTES
# ============================================================

session_ids = [
    f"S{i:05d}"
    for i in range(1, N_SESSIONS + 1)
]

user_ids = [
    f"U{i:05d}"
    for i in range(1, N_SESSIONS + 1)
]

devices = np.random.choice(
    ["Desktop", "Mobile", "Tablet"],
    size=N_SESSIONS,
    p=[0.36, 0.52, 0.12]
)

traffic_sources = np.random.choice(
    [
        "Organic Search",
        "Direct",
        "Email",
        "Paid Search",
        "Social",
        "Referral"
    ],
    size=N_SESSIONS,
    p=[0.25, 0.18, 0.10, 0.18, 0.17, 0.12]
)

regions = np.random.choice(
    ["North", "South", "East", "West", "Central"],
    size=N_SESSIONS,
    p=[0.20, 0.20, 0.20, 0.20, 0.20]
)

categories = [
    "Electronics",
    "Fashion",
    "Home",
    "Beauty",
    "Sports"
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def choose_category():
    return np.random.choice(categories)


def generate_session_events(
    session_id,
    user_id,
    device,
    source,
    region,
    start_time
):

    events = []

    category = choose_category()

    # --------------------------------------------------------
    # Base browsing engagement
    # --------------------------------------------------------

    pages_viewed = np.random.poisson(2.0) + 1

    if device == "Mobile":
        pages_viewed += np.random.binomial(1, 0.25)

    if source in ["Email", "Direct"]:
        pages_viewed += np.random.binomial(1, 0.30)

    pages_viewed = max(1, pages_viewed)

    # --------------------------------------------------------
    # Generate product views
    # --------------------------------------------------------

    current_time = start_time

    events.append({
        "user_id": user_id,
        "session_id": session_id,
        "event_time": current_time,
        "event_type": "product_view",
        "device_type": device,
        "traffic_source": source,
        "region": region,
        "product_category": category,
        "order_value": np.nan
    })

    for _ in range(pages_viewed - 1):

        current_time += timedelta(
            seconds=int(np.random.randint(20, 180))
        )

        if np.random.rand() < 0.30:
            category = choose_category()

        events.append({
            "user_id": user_id,
            "session_id": session_id,
            "event_time": current_time,
            "event_type": "product_view",
            "device_type": device,
            "traffic_source": source,
            "region": region,
            "product_category": category,
            "order_value": np.nan
        })

    # --------------------------------------------------------
    # Add-to-cart probability
    # --------------------------------------------------------

    cart_probability = 0.22

    if pages_viewed >= 3:
        cart_probability += 0.12

    if source in ["Email", "Direct"]:
        cart_probability += 0.06

    if source == "Social":
        cart_probability -= 0.04

    if device == "Mobile":
        cart_probability -= 0.02

    cart_probability = np.clip(
        cart_probability,
        0.05,
        0.70
    )

    added_to_cart = np.random.rand() < cart_probability

    if not added_to_cart:
        return events

    # --------------------------------------------------------
    # Add to cart
    # --------------------------------------------------------

    current_time += timedelta(
        seconds=int(np.random.randint(30, 240))
    )

    events.append({
        "user_id": user_id,
        "session_id": session_id,
        "event_time": current_time,
        "event_type": "add_to_cart",
        "device_type": device,
        "traffic_source": source,
        "region": region,
        "product_category": category,
        "order_value": np.nan
    })

    # --------------------------------------------------------
    # Checkout probability
    # --------------------------------------------------------

    checkout_probability = 0.55

    if source in ["Email", "Direct"]:
        checkout_probability += 0.08

    if source == "Social":
        checkout_probability -= 0.08

    if device == "Mobile":
        checkout_probability -= 0.05

    checkout_probability = np.clip(
        checkout_probability,
        0.10,
        0.90
    )

    started_checkout = (
        np.random.rand() < checkout_probability
    )

    if not started_checkout:
        return events

    # --------------------------------------------------------
    # Checkout
    # --------------------------------------------------------

    current_time += timedelta(
        seconds=int(np.random.randint(60, 300))
    )

    events.append({
        "user_id": user_id,
        "session_id": session_id,
        "event_time": current_time,
        "event_type": "checkout_start",
        "device_type": device,
        "traffic_source": source,
        "region": region,
        "product_category": category,
        "order_value": np.nan
    })

    # --------------------------------------------------------
    # Purchase probability
    # --------------------------------------------------------

    purchase_probability = 0.48

    if source in ["Email", "Direct"]:
        purchase_probability += 0.07

    if source == "Social":
        purchase_probability -= 0.06

    if device == "Mobile":
        purchase_probability -= 0.04

    if pages_viewed >= 4:
        purchase_probability += 0.08

    purchase_probability = np.clip(
        purchase_probability,
        0.10,
        0.90
    )

    purchased = (
        np.random.rand() < purchase_probability
    )

    if purchased:

        current_time += timedelta(
            seconds=int(np.random.randint(60, 360))
        )

        order_value = round(
            np.random.lognormal(
                mean=4.0,
                sigma=0.55
            ),
            2
        )

        events.append({
            "user_id": user_id,
            "session_id": session_id,
            "event_time": current_time,
            "event_type": "purchase",
            "device_type": device,
            "traffic_source": source,
            "region": region,
            "product_category": category,
            "order_value": order_value
        })

    return events


# ============================================================
# GENERATE EVENTS
# ============================================================

all_events = []

base_time = datetime(
    2026,
    1,
    1,
    8,
    0,
    0
)

for i in range(N_SESSIONS):

    session_start = (
        base_time
        + timedelta(
            minutes=int(
                np.random.randint(
                    0,
                    60 * 24 * 30
                )
            )
        )
    )

    events = generate_session_events(
        session_ids[i],
        user_ids[i],
        devices[i],
        traffic_sources[i],
        regions[i],
        session_start
    )

    all_events.extend(events)


# ============================================================
# CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(all_events)

df = df.sort_values(
    ["session_id", "event_time"]
).reset_index(drop=True)


# ============================================================
# SAVE DATASET
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\nDataset generated successfully.")

print("\nNumber of sessions:")
print(df["session_id"].nunique())

print("\nNumber of events:")
print(len(df))

print("\nEvent distribution:")
print(
    df["event_type"]
    .value_counts()
)

print("\nConversion rate:")

purchase_sessions = (
    df.groupby("session_id")["event_type"]
    .apply(
        lambda x: int(
            "purchase" in x.values
        )
    )
)

print(
    purchase_sessions.mean()
)

print("\nSaved to:")
print(OUTPUT_FILE)