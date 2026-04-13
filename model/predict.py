import pickle
import numpy as np
import os

# Get absolute path to model file
MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "fraud_model.pkl"
)

# Load model once during startup
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)


def predict_transaction(transaction):
    transaction = np.array(transaction).reshape(1, -1)

    # Isolation Forest anomaly score
    score = model.decision_function(transaction)[0]

    # Convert to risk %
    risk_score = round((1 - score) * 50, 2)
    risk_score = max(0, min(100, risk_score))

    prediction = "Fraud" if score < 0 else "Normal"

    return prediction, risk_score