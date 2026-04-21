import pickle
import pandas as pd
import os

# ===== LOAD MODELS SAFELY =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "../model/xgb_model.pkl"), "rb") as f:
    xgb_model = pickle.load(f)

with open(os.path.join(BASE_DIR, "../model/iso_model.pkl"), "rb") as f:
    anomaly_model = pickle.load(f)

with open(os.path.join(BASE_DIR, "../model/preprocessor.pkl"), "rb") as f:
    preprocessor = pickle.load(f)


# ===== HYBRID PREDICTION FUNCTION =====
def hybrid_predict(raw_data):

    # ✅ Convert JSON → DataFrame
    input_df = pd.DataFrame([raw_data])

    # ===== XGBOOST =====
    try:
        xgb_prob = xgb_model.predict_proba(input_df)[0][1]
    except Exception as e:
        raise ValueError(f"XGBoost prediction error: {str(e)}")

    xgb_score = round(float(xgb_prob) * 100, 2)

    # ===== ANOMALY DETECTION =====
    try:
        X_processed = preprocessor.transform(input_df)
        anomaly_raw = anomaly_model.decision_function(X_processed)[0]

        anomaly_score = round((1 - float(anomaly_raw)) * 50, 2)
        anomaly_score = max(0, min(100, anomaly_score))

    except Exception as e:
        raise ValueError(f"Anomaly model error: {str(e)}")

    # ===== RULE ENGINE =====
    rule_score = 0
    reasons = []

    if raw_data.get("amount", 0) > 50000:
        rule_score += 25
        reasons.append("High transaction amount")

    if raw_data.get("foreign_transaction", 0) == 1:
        rule_score += 20
        reasons.append("Foreign transaction")

    if raw_data.get("location_mismatch", 0) == 1:
        rule_score += 15
        reasons.append("Location mismatch")

    if raw_data.get("device_trust_score", 1) < 0.3:
        rule_score += 20
        reasons.append("Low device trust")

    if raw_data.get("velocity_last_24h", 0) > 10:
        rule_score += 10
        reasons.append("High transaction velocity")

    rule_score = min(100, rule_score)

    # ===== FINAL SCORE =====
    final_score = round(
        (0.6 * xgb_score) +
        (0.25 * anomaly_score) +
        (0.15 * rule_score),
        2
    )

    prediction = "Fraud" if final_score > 60 else "Normal"

    # ===== RETURN CLEAN (Mongo-safe types) =====
    return {
        "prediction": str(prediction),
        "risk_score": float(final_score),
        "xgb_score": float(xgb_score),
        "anomaly_score": float(anomaly_score),
        "rule_score": float(rule_score),
        "reasons": [str(r) for r in reasons]
    }