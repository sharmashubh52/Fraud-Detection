def build_feature_vector(data):

    categories = [
        "Electronics",
        "Food",
        "Travel",
        "Clothing",
        "Health"
    ]

    features = [
        data["amount"],
        data["transaction_hour"],
        data["foreign_transaction"],
        data["location_mismatch"],
        data["device_trust_score"],
        data["velocity_last_24h"],
        data["cardholder_age"]
    ]

    # One-hot encoding for merchant category
    for cat in categories:
        if data["merchant_category"] == cat:
            features.append(1)
        else:
            features.append(0)

    return features
