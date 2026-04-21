import requests
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

API_URL = "https://fraud-detection-yrkn.onrender.com/check_transaction"

CATEGORIES = ["Electronics", "Food", "Travel", "Clothing", "Health"]


# ===== GENERATE REALISTIC TRANSACTION =====
def generate_transaction():
    is_fraud_like = random.random() < 0.2  # 20% fraud-like behavior

    return {
        "amount": round(random.uniform(500, 100000 if is_fraud_like else 20000), 2),
        "transaction_hour": random.randint(0, 23),
        "foreign_transaction": 1 if is_fraud_like and random.random() > 0.5 else 0,
        "location_mismatch": 1 if is_fraud_like and random.random() > 0.5 else 0,
        "device_trust_score": round(random.uniform(0.1, 0.5) if is_fraud_like else random.uniform(0.6, 1.0), 2),
        "velocity_last_24h": random.randint(5, 20) if is_fraud_like else random.randint(0, 5),
        "cardholder_age": random.randint(18, 70),
        "merchant_category": random.choice(CATEGORIES),
    }


# ===== SINGLE REQUEST =====
def send_request(i):
    payload = generate_transaction()

    try:
        res = requests.post(API_URL, json=payload, timeout=10)

        if res.status_code == 200:
            return "success"
        else:
            return "failed"

    except:
        return "failed"


# ===== MAIN SIMULATION =====
def run_simulation(total=5000, workers=15):
    success = 0
    failed = 0

    print(f"\n🚀 Running {total} transactions with {workers} workers...\n")

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(send_request, i) for i in range(total)]

        for i, future in enumerate(as_completed(futures)):
            result = future.result()

            if result == "success":
                success += 1
            else:
                failed += 1

            # Progress log
            if (i + 1) % 100 == 0:
                print(f"Processed: {i+1} | Success: {success} | Failed: {failed}")

    print("\n===== FINAL RESULT =====")
    print(f"✅ Success: {success}")
    print(f"❌ Failed: {failed}")


# ===== RUN =====
if __name__ == "__main__":
    run_simulation(total=5000, workers=15)