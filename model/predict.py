import pickle
import numpy as np

# ===== LOAD MODELS =====
with open("model/fraud_model.pkl", "rb") as f:
    anomaly_model = pickle.load(f)

with open("model/xgb_model.pkl", "rb") as f:
    xgb_model = pickle.load(f)


# ===== HYBRID PREDICTION FUNCTION =====
def hybrid_predict(transaction):

    transaction = np.array(transaction).reshape(1, -1)

    # ---- XGBoost (Supervised) ----
    xgb_prob = xgb_model.predict_proba(transaction)[0][1]   # probability of fraud
    xgb_score = round(xgb_prob * 100, 2)

    # ---- Isolation Forest (Anomaly) ----
    anomaly_score_raw = anomaly_model.decision_function(transaction)[0]
    anomaly_score = round((1 - anomaly_score_raw) * 50, 2)

    # Clamp
    anomaly_score = max(0, min(100, anomaly_score))

    # ---- FINAL WEIGHTED SCORE ----
    final_score = round((0.7 * xgb_score) + (0.3 * anomaly_score), 2)

    # ---- FINAL DECISION ----
    if final_score > 60:
        prediction = "Fraud"
    else:
        prediction = "Normal"

    return {
        "prediction": prediction,
        "risk_score": final_score,
        "xgb_score": xgb_score,
        "anomaly_score": anomaly_score
    }