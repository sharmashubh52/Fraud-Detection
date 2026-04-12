import pickle
import numpy as np

# Load model
with open("model/fraud_model.pkl", "rb") as f:
    model = pickle.load(f)

def predict_transaction(transaction):

    transaction = np.array(transaction).reshape(1, -1)

    # Get anomaly score
    score = model.decision_function(transaction)[0]

    # Convert to risk percentage
    risk_score = round((1 - score) * 50, 2)

    # Clamp between 0–100
    risk_score = max(0, min(100, risk_score))

    # Determine label
    if score < 0:
        prediction = "Fraud"
    else:
        prediction = "Normal"

    return prediction, risk_score
