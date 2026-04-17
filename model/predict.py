import pickle
import numpy as np

# ===== LOAD MODELS =====
with open("model/fraud_model.pkl", "rb") as f:
    anomaly_model = pickle.load(f)

with open("model/xgb_model.pkl", "rb") as f:
    xgb_model = pickle.load(f)


def hybrid_predict(transaction):

    transaction = np.array(transaction).reshape(1, -1)

    # ===== XGBOOST (Supervised) =====
    xgb_prob = xgb_model.predict_proba(transaction)[0][1]
    xgb_score = round(xgb_prob * 100, 2)

    # ===== ANOMALY (Isolation Forest) =====
    anomaly_raw = anomaly_model.decision_function(transaction)[0]
    anomaly_score = round((1 - anomaly_raw) * 50, 2)
    anomaly_score = max(0, min(100, anomaly_score))

    # ===== RULE ENGINE =====
    rule_score = 0
    reasons = []

    amount = transaction[0][0]
    device_score = transaction[0][4]

    if amount > 50000:
        rule_score += 25
        reasons.append("High transaction amount")

    if device_score < 0.3:
        rule_score += 20
        reasons.append("Low device trust")

    rule_score = min(100, rule_score)

    # ===== FINAL WEIGHTED SCORE =====
    final_score = round(
        (0.6 * xgb_score) +
        (0.25 * anomaly_score) +
        (0.15 * rule_score),
        2
    )

    # ===== FINAL DECISION =====
    prediction = "Fraud" if final_score > 60 else "Normal"

    return {
        "prediction": prediction,
        "risk_score": final_score,
        "xgb_score": xgb_score,
        "anomaly_score": anomaly_score,
        "rule_score": rule_score,
        "reasons": reasons
    }