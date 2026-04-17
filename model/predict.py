import os
import pickle
import numpy as np

# ================= LOAD MODELS =================
with open("model/xgb_model.pkl", "rb") as f:
    xgb_model = pickle.load(f)

with open("model/iso_model.pkl", "rb") as f:
    iso_model = pickle.load(f)

with open("model/preprocessor.pkl", "rb") as f:
    preprocessor = pickle.load(f)


# ================= RULE ENGINE =================
def rule_engine(data):
    score = 0
    reasons = []

    if data.get("amount", 0) > 50000:
        score += 30
        reasons.append("High transaction amount")

    if data.get("foreign_transaction", 0) == 1:
        score += 25
        reasons.append("Foreign transaction")

    if data.get("location_mismatch", 0) == 1:
        score += 25
        reasons.append("Location mismatch")

    if data.get("device_trust_score", 1) < 0.3:
        score += 20
        reasons.append("Low device trust")

    return min(score, 100), reasons


# ================= MAIN FUNCTION =================
def predict_transaction(data):
    try:
        # ================= PREPARE INPUT =================
        features = [data]  # model expects list of dicts

        # ================= XGBOOST =================
        xgb_prob = xgb_model.predict_proba(features)[0][1]
        xgb_score = round(xgb_prob * 100, 2)

        # ================= PREPROCESS =================
        processed = preprocessor.transform(features)

        # ================= ANOMALY =================
        anomaly_raw = iso_model.decision_function(processed)[0]

        anomaly_score = (1 - anomaly_raw) * 50
        anomaly_score = round(max(0, min(100, anomaly_score)), 2)

        # ================= RULE ENGINE =================
        rule_score, reasons = rule_engine(data)

        # ================= FINAL SCORE =================
        final_score = (
            0.5 * xgb_score +
            0.3 * anomaly_score +
            0.2 * rule_score
        )

        final_score = round(min(100, final_score), 2)

        # ================= DECISION =================
        prediction = "Fraud" if final_score > 60 else "Normal"

        return {
            "prediction": prediction,
            "risk_score": final_score,
            "xgb_score": xgb_score,
            "anomaly_score": anomaly_score,
            "rule_score": rule_score,
            "reasons": reasons
        }

    except Exception as e:
        # VERY IMPORTANT FOR DEBUGGING
        print("PREDICTION ERROR:", str(e))
        raise e