import pandas as pd
from sklearn.ensemble import IsolationForest
import pickle
import sys
import os

# Allow import from utils folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.preprocess import preprocess_data


# Load and preprocess data
data = preprocess_data("data/credit_card_fraud_10k.csv")

# Remove target column if exists
if "is_fraud" in data.columns:
    X = data.drop("is_fraud", axis=1)
else:
    X = data

# Train model
model = IsolationForest(contamination=0.02, random_state=42)
model.fit(X)

# Save model
with open("model/fraud_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Model trained and saved successfully!")
