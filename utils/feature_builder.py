def build_feature_vector(data):
    return [
        data.get("amount", 0),
        data.get("transaction_hour", 0),
        data.get("foreign_transaction", 0),
        data.get("location_mismatch", 0),
        data.get("device_trust_score", 0),
        data.get("velocity_last_24h", 0),
        data.get("cardholder_age", 0),

        # Encode category manually (IMPORTANT)
        encode_category(data.get("merchant_category", "Other"))
    ]


def encode_category(category):
    mapping = {
        "Electronics": 1,
        "Food": 2,
        "Travel": 3,
        "Clothing": 4,
        "Health": 5
    }
    return mapping.get(category, 0)