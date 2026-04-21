# utils/feature_builder.py

def build_feature_vector(data):

    amount = float(data.get("amount", 0))
    hour = int(data.get("transaction_hour", 0))
    foreign = int(data.get("foreign_transaction", 0))
    mismatch = int(data.get("location_mismatch", 0))
    device = float(data.get("device_trust_score", 0))
    velocity = int(data.get("velocity_last_24h", 0))
    age = int(data.get("cardholder_age", 0))
    category = data.get("merchant_category", "Other")

    # ===== CATEGORY ENCODING =====
    category_map = {
        "Electronics": 0,
        "Food": 1,
        "Travel": 2,
        "Clothing": 3,
        "Health": 4
    }
    category_encoded = category_map.get(category, 5)

    # ===== EXTRA FEATURE (to match 9 features) =====
    is_night = 1 if (hour >= 22 or hour <= 5) else 0

    # ===== FINAL VECTOR (9 FEATURES) =====
    features = [
        amount,
        hour,
        foreign,
        mismatch,
        device,
        velocity,
        age,
        category_encoded,
        is_night
    ]

    return features