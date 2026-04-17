import pandas as pd
import numpy as np
import pickle
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report

from xgboost import XGBClassifier

# ================= LOAD DATA =================
df = pd.read_csv("data/credit_card_fraud_10k.csv")

# ================= FEATURES =================
X = df.drop("is_fraud", axis=1)
y = df["is_fraud"]

# ================= COLUMNS =================
numeric_features = [
    "amount",
    "transaction_hour",
    "device_trust_score",
    "velocity_last_24h",
    "cardholder_age"
]

categorical_features = [
    "merchant_category"
]

binary_features = [
    "foreign_transaction",
    "location_mismatch"
]

# ================= PREPROCESSING =================
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_features),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ("bin", "passthrough", binary_features)
    ]
)

# ================= XGBOOST MODEL =================
xgb_model = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=5,   # handles imbalance
        random_state=42
    ))
])

# ================= TRAIN TEST SPLIT =================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ================= TRAIN =================
xgb_model.fit(X_train, y_train)

# ================= EVALUATION =================
y_pred = xgb_model.predict(X_test)
print("\nXGBoost Performance:\n")
print(classification_report(y_test, y_pred))

# ================= ISOLATION FOREST =================
# Use ONLY features (no labels)
X_processed = preprocessor.fit_transform(X)

iso_model = IsolationForest(
    n_estimators=100,
    contamination=0.05,
    random_state=42
)

iso_model.fit(X_processed)

# ================= SAVE MODELS =================
os.makedirs("model", exist_ok=True)

with open("model/xgb_model.pkl", "wb") as f:
    pickle.dump(xgb_model, f)

with open("model/iso_model.pkl", "wb") as f:
    pickle.dump(iso_model, f)

with open("model/preprocessor.pkl", "wb") as f:
    pickle.dump(preprocessor, f)

print("\n✅ Models trained and saved successfully!")