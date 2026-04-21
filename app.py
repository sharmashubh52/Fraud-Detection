from flask import Flask, request, jsonify
from model.predict import hybrid_predict
from utils.db import transactions_collection
import os
import logging

app = Flask(__name__)

# ===== LOGGING SETUP =====
logging.basicConfig(level=logging.INFO)

# ===== HEALTH CHECK =====
@app.route("/")
def home():
    return jsonify({"message": "Fraud Detection API Running"})

# ===== MAIN ENDPOINT =====
@app.route("/check_transaction", methods=["POST"])
def check_transaction():
    try:
        data = request.get_json()

        # ===== BASIC VALIDATION =====
        required_fields = [
            "amount",
            "transaction_hour",
            "merchant_category",
            "foreign_transaction",
            "location_mismatch",
            "device_trust_score",
            "velocity_last_24h",
            "cardholder_age"
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        # ===== LOG INPUT =====
        logging.info(f"Incoming request: {data}")

        # ===== PREDICTION (NO FEATURE BUILDER) =====
        result = hybrid_predict(data)

        # ===== STORE IN DB =====
        record = data.copy()
        record.update(result)

        transactions_collection.insert_one(record)

        # ===== LOG OUTPUT =====
        logging.info(f"Prediction result: {result}")

        return jsonify(result)

    except Exception as e:
        logging.error(f"ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ===== RUN APP =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)