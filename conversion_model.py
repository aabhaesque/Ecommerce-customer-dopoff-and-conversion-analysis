import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_auc_score,
    classification_report,
    confusion_matrix
)


# ============================================================
# 1. LOAD DATA
# ============================================================

df = pd.read_csv(
    "data/ecommerce_user_events.csv"
)

df["event_time"] = pd.to_datetime(
    df["event_time"]
)

df = df.sort_values(
    ["session_id", "event_time"]
)


# ============================================================
# 2. DEFINE THE 5-MINUTE OBSERVATION WINDOW
# ============================================================

session_start = (
    df.groupby("session_id")["event_time"]
    .min()
    .rename("session_start")
)

df = df.merge(
    session_start,
    on="session_id",
    how="left"
)

df["minutes_from_start"] = (
    df["event_time"] - df["session_start"]
).dt.total_seconds() / 60

early_df = df[
    df["minutes_from_start"] <= 5
].copy()


# ============================================================
# 3. CREATE THE CONVERSION TARGET
# ============================================================

conversion_target = (
    df.groupby("session_id")["event_type"]
    .apply(
        lambda x: int(
            "purchase" in x.values
        )
    )
    .rename("converted")
)


# ============================================================
# 4. EARLY-SESSION FEATURES
# ============================================================

early_features = (
    early_df
    .groupby("session_id")
    .agg(
        early_events=("event_type", "count"),

        early_product_views=(
            "event_type",
            lambda x: (x == "product_view").sum()
        ),

        early_unique_categories=(
            "product_category",
            "nunique"
        ),

        early_event_types=(
            "event_type",
            "nunique"
        ),

        device_type=(
            "device_type",
            "first"
        ),

        traffic_source=(
            "traffic_source",
            "first"
        ),

        region=(
            "region",
            "first"
        )
    )
)


# ============================================================
# 5. EARLY-SESSION DURATION
# ============================================================

early_duration = (
    early_df
    .groupby("session_id")["event_time"]
    .agg(
        lambda x:
        (
            x.max() - x.min()
        ).total_seconds() / 60
    )
    .rename("early_duration_min")
)


early_features = early_features.join(
    early_duration
)


# ============================================================
# 6. COMBINE FEATURES + TARGET
# ============================================================

session_df = (
    early_features
    .join(conversion_target)
    .reset_index()
)


# Fill sessions with no events inside the first
# five-minute window.

numeric_fill_columns = [
    "early_events",
    "early_product_views",
    "early_unique_categories",
    "early_event_types",
    "early_duration_min"
]

session_df[numeric_fill_columns] = (
    session_df[numeric_fill_columns]
    .fillna(0)
)


# ============================================================
# 7. DISPLAY DATASET
# ============================================================

print("\nEarly-session modelling dataset:")

print(
    session_df.head()
)

print("\nDataset shape:")

print(
    session_df.shape
)

print("\nConversion distribution:")

print(
    session_df["converted"]
    .value_counts()
)

print("\nConversion rate:")

print(
    session_df["converted"].mean()
)


# ============================================================
# 8. MODEL FEATURES
# ============================================================

numeric_features = [
    "early_events",
    "early_product_views",
    "early_unique_categories",
    "early_event_types",
    "early_duration_min"
]

categorical_features = [
    "device_type",
    "traffic_source",
    "region"
]

feature_columns = (
    numeric_features
    + categorical_features
)


X = session_df[
    feature_columns
]

y = session_df[
    "converted"
]


# ============================================================
# 9. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = (
    train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )
)


# ============================================================
# 10. PREPROCESSING
# ============================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            StandardScaler(),
            numeric_features
        ),

        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categorical_features
        )
    ]
)


# ============================================================
# 11. LOGISTIC REGRESSION
# ============================================================

model = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),

        (
            "classifier",
            LogisticRegression(
                max_iter=1000,
                class_weight="balanced"
            )
        )
    ]
)


# ============================================================
# 12. TRAIN MODEL
# ============================================================

model.fit(
    X_train,
    y_train
)


# ============================================================
# 13. PREDICTIONS
# ============================================================

y_pred = model.predict(
    X_test
)

y_prob = model.predict_proba(
    X_test
)[:, 1]


# ============================================================
# 14. MODEL EVALUATION
# ============================================================

auc = roc_auc_score(
    y_test,
    y_prob
)


print(
    "\n" + "=" * 55
)

print(
    "EARLY-SESSION LOGISTIC REGRESSION"
)

print(
    "=" * 55
)

print(
    f"\nROC-AUC: {auc:.3f}"
)

print(
    "\nClassification Report:"
)

print(
    classification_report(
        y_test,
        y_pred,
        zero_division=0
    )
)

print(
    "\nConfusion Matrix:"
)

print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# ============================================================
# 15. FEATURE IMPORTANCE
# ============================================================

feature_names = (
    model
    .named_steps["preprocessor"]
    .get_feature_names_out()
)

coefficients = (
    model
    .named_steps["classifier"]
    .coef_[0]
)

feature_importance = pd.DataFrame({
    "feature": feature_names,
    "coefficient": coefficients
})

feature_importance[
    "absolute_importance"
] = (
    feature_importance[
        "coefficient"
    ].abs()
)

feature_importance = (
    feature_importance
    .sort_values(
        "absolute_importance",
        ascending=False
    )
)


print(
    "\nTop Conversion Drivers:"
)

print(
    feature_importance
    .head(15)
    .to_string(index=False)
)


# ============================================================
# 16. BEHAVIOURAL COMPARISON
# ============================================================

print(
    "\nBehaviour by Conversion:"
)

print(
    session_df
    .groupby("converted")[
        numeric_features
    ]
    .mean()
)


# ============================================================
# 17. SAVE OUTPUTS
# ============================================================

session_df.to_csv(
    "outputs/session_features.csv",
    index=False
)

feature_importance.to_csv(
    "outputs/feature_importance.csv",
    index=False
)

metrics = pd.DataFrame({
    "metric": [
        "ROC-AUC",
        "Conversion Rate"
    ],

    "value": [
        auc,
        session_df[
            "converted"
        ].mean()
    ]
})

metrics.to_csv(
    "outputs/model_metrics.csv",
    index=False
)


print(
    "\nOutputs saved successfully:"
)

print(
    "- outputs/session_features.csv"
)

print(
    "- outputs/feature_importance.csv"
)

print(
    "- outputs/model_metrics.csv"
)