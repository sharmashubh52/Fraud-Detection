def calculate_rule_score(data):
    score = 0
    reasons = []

    if data["amount"] > 50000:
        score += 20
        reasons.append("High transaction amount")

    if data["foreign_transaction"] == 1:
        score += 20
        reasons.append("Foreign transaction")

    if data["location_mismatch"] == 1:
        score += 15
        reasons.append("Location mismatch")

    if data["device_trust_score"] < 0.3:
        score += 20
        reasons.append("Low device trust")

    if data["velocity_last_24h"] > 5:
        score += 15
        reasons.append("High transaction velocity")

    return min(score, 100), reasons