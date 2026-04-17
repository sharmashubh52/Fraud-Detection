from flask import Flask, request, jsonify
from model.predict import hybrid_predict
from utils.feature_builder import build_feature_vector
from utils.db import transactions_collection
import os

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "Fraud Detection API Running"})


@app.route("/check_transaction", methods=["POST"])
def check_transaction():
    try:
        data = request.get_json()

        # ✅ Step 1: Feature Engineering
        features = build_feature_vector(data)

        # ✅ Step 2: Hybrid Prediction
        result = hybrid_predict(features, data)

        # ✅ Step 3: Save to MongoDB
        record = data.copy()
        record.update(result)

        transactions_collection.insert_one(record)

        # ✅ Step 4: Return response
        return jsonify(result)

    except Exception as e:
        print("ERROR:", str(e))  # helpful for Render logs
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)