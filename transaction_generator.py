import requests
import random
import time

categories = ["Electronics", "Food", "Travel", "Clothing", "Health"]

while True:
    payload = {
        "amount": random.randint(50, 90000),
        "transaction_hour": random.randint(0, 23),
        "foreign_transaction": random.choice([0, 1]),
        "location_mismatch": random.choice([0, 1]),
        "device_trust_score": round(random.uniform(0.05, 0.95), 2),
        "velocity_last_24h": random.randint(1, 25),
        "cardholder_age": random.randint(18, 65),
        "merchant_category": random.choice(categories)
    }

    requests.post(
        "http://127.0.0.1:5000/check_transaction",
        json=payload
    )

    print("Sent:", payload)
    time.sleep(1)