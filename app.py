from flask import Flask, request, jsonify
from model.predict import predict_transaction
from utils.feature_builder import build_feature_vector
from utils.db import transactions_collection
import os

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "Fraud Detection API Running"})

@app.route("/check_transaction", methods=["POST"])
def check_transaction():
    data = request.json

    features = build_feature_vector(data)
    prediction, risk_score = predict_transaction(features)

    record = data.copy()
    record["prediction"] = prediction
    record["risk_score"] = risk_score

    transactions_collection.insert_one(record)

    return jsonify({
        "prediction": prediction,
        "risk_score": risk_score
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)