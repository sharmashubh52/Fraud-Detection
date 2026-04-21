import pandas as pd
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

# ================= PREPROCESSOR =================
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_features),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ("bin", "passthrough", binary_features)
    ]
)

# ================= XGBOOST PIPELINE =================
xgb_pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=5,
        random_state=42
    ))
])

# ================= TRAIN TEST SPLIT =================
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# ================= TRAIN MODEL =================
xgb_pipeline.fit(X_train, y_train)

# ================= EVALUATION =================
y_pred = xgb_pipeline.predict(X_test)

print("\nXGBoost Performance:\n")
print(classification_report(y_test, y_pred))

# ================= GET TRAINED PREPROCESSOR =================
trained_preprocessor = xgb_pipeline.named_steps["preprocessor"]

# ================= TRANSFORM DATA FOR ISOLATION FOREST =================
X_processed = trained_preprocessor.transform(X)

# ================= ISOLATION FOREST =================
iso_model = IsolationForest(
    n_estimators=100,
    contamination=0.05,
    random_state=42
)

iso_model.fit(X_processed)

# ================= SAVE MODELS =================
os.makedirs("model", exist_ok=True)

# Save full pipeline (best practice)
with open("model/xgb_model.pkl", "wb") as f:
    pickle.dump(xgb_pipeline, f)

# Save Isolation Forest
with open("model/iso_model.pkl", "wb") as f:
    pickle.dump(iso_model, f)

# Save SAME preprocessor used in pipeline
with open("model/preprocessor.pkl", "wb") as f:
    pickle.dump(trained_preprocessor, f)

print("\n✅ Models trained and saved successfully!")