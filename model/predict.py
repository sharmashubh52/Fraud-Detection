import pickle
import numpy as np

# ===== LOAD MODELS =====
with open("model/fraud_model.pkl", "rb") as f:
    anomaly_model = pickle.load(f)

with open("model/xgb_model.pkl", "rb") as f:
    xgb_model = pickle.load(f)


# ===== HYBRID PREDICT =====
def hybrid_predict(features, raw_data):

    # Convert to numpy
    X = np.array(features).reshape(1, -1)

    # ✅ FIX: Feature size validation (prevents 12 vs 9 error)
    if hasattr(xgb_model, "n_features_in_"):
        if X.shape[1] != xgb_model.n_features_in_:
            raise ValueError(
                f"Feature mismatch: Expected {xgb_model.n_features_in_}, got {X.shape[1]}"
            )

    # ===== XGBOOST =====
    xgb_prob = xgb_model.predict_proba(X)[0][1]
    xgb_score = round(xgb_prob * 100, 2)

    # ===== ANOMALY =====
    anomaly_raw = anomaly_model.decision_function(X)[0]
    anomaly_score = round((1 - anomaly_raw) * 50, 2)
    anomaly_score = max(0, min(100, anomaly_score))

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

    rule_score = min(100, rule_score)

    # ===== FINAL SCORE =====
    final_score = round(
        (0.6 * xgb_score) +
        (0.25 * anomaly_score) +
        (0.15 * rule_score),
        2
    )

    prediction = "Fraud" if final_score > 60 else "Normal"

    return {
        "prediction": prediction,
        "risk_score": final_score,
        "xgb_score": xgb_score,
        "anomaly_score": anomaly_score,
        "rule_score": rule_score,
        "reasons": reasons
    }