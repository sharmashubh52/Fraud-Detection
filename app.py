from flask import Flask, request, jsonify
from model.predict import hybrid_predict
from utils.db import transactions_collection
import os
import logging

app = Flask(__name__)

# ===== LOGGING =====
logging.basicConfig(level=logging.INFO)


# ===== CLEAN NUMPY TYPES (Mongo Fix) =====
def clean_numpy_types(obj):
    import numpy as np

    if isinstance(obj, dict):
        return {k: clean_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_numpy_types(i) for i in obj]
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    else:
        return obj


# ===== HEALTH CHECK =====
@app.route("/")
def home():
    return jsonify({"message": "Fraud Detection API Running"})


# ===== MAIN ENDPOINT =====
@app.route("/check_transaction", methods=["POST"])
def check_transaction():
    try:
        data = request.get_json()

        # ✅ Validate JSON
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400

        # ✅ Required fields
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

        logging.info(f"Incoming request: {data}")

        # ===== PREDICTION =====
        result = hybrid_predict(data)

        # ===== STORE IN DB =====
        record = data.copy()
        record.update(result)

        # ✅ Clean numpy types before insert
        record = clean_numpy_types(record)

        try:
            transactions_collection.insert_one(record)
        except Exception as db_error:
            logging.error(f"MongoDB insert failed: {str(db_error)}")

        logging.info(f"Prediction result: {result}")

        return jsonify(result)

    except Exception as e:
        logging.error(f"ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ===== RUN APP =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)