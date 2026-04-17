import pickle
import numpy as np
import os
from utils.rule_engine import calculate_rule_score

# Paths
BASE_DIR = os.path.dirname(__file__)

with open(os.path.join(BASE_DIR, "xgb_model.pkl"), "rb") as f:
    xgb_model = pickle.load(f)

with open(os.path.join(BASE_DIR, "iso_model.pkl"), "rb") as f:
    iso_model = pickle.load(f)


def hybrid_predict(features, raw_data):
    features = [features]  # keep as list, pipeline will handle it

    # 1️⃣ XGBoost probability
    xgb_prob = xgb_model.predict_proba(features)[0][1] * 100

    # 2️⃣ Isolation Forest anomaly
    iso_score_raw = iso_model.decision_function(features)[0]
    iso_score = max(0, min(100, (1 - iso_score_raw) * 50))

    # 3️⃣ Rule Engine
    rule_score, reasons = calculate_rule_score(raw_data)

    # 4️⃣ Final weighted score
    final_score = round(
        0.5 * xgb_prob +
        0.3 * iso_score +
        0.2 * rule_score,
        2
    )

    prediction = "Fraud" if final_score > 65 else "Normal"

    return {
        "prediction": prediction,
        "risk_score": final_score,
        "xgb_score": round(xgb_prob, 2),
        "anomaly_score": round(iso_score, 2),
        "rule_score": rule_score,
        "reasons": reasons
    }