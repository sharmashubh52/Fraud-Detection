import streamlit as st
import requests
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import time

st.set_page_config(page_title="FraudShield AI", page_icon="💳", layout="wide")

# ================= PREMIUM THEME =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0b1220 0%, #111827 100%);
    color: white;
}
.block-container {
    padding-top: 1.5rem;
}
div[data-testid="stMetric"] {
    background: rgba(17, 24, 39, 0.9);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 18px;
    border-radius: 18px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.25);
}
</style>
""", unsafe_allow_html=True)

API_URL = os.getenv("API_URL", "https://fraud-detection-yrkn.onrender.com/check_transaction")
MONGO_URI = os.getenv("MONGO_URI")

st.title("💳 FraudShield AI — Premium Risk Intelligence")
st.caption("Real-time fraud scoring • cloud-native analytics • fintech-grade observability")

page = st.sidebar.radio("Workspace", ["💳 Transaction Simulator", "📊 Risk Command Center"])

# ================= CUSTOMER =================
if page == "💳 Transaction Simulator":
    st.subheader("💸 Smart Transaction Risk Analyzer")

    top1, top2, top3 = st.columns(3)
    top1.metric("Avg Approval Rate", "96.4%")
    top2.metric("Fraud Detection SLA", "< 2 sec")
    top3.metric("System Status", "🟢 Live")

    col1, col2 = st.columns(2)

    with col1:
        amount = st.number_input("Amount (₹)", min_value=0.0, value=1000.0)
        hour = st.slider("Transaction Hour", 0, 23, 12)
        age = st.number_input("Cardholder Age", 18, 100, 30)

    with col2:
        foreign = st.selectbox("Foreign Transaction", ["No", "Yes"])
        mismatch = st.selectbox("Location Mismatch", ["No", "Yes"])
        device_score = st.slider("Device Trust Score", 0.0, 1.0, 0.8)

    velocity = st.number_input("Transactions in Last 24h", 0, 50, 1)
    category = st.selectbox(
        "Merchant Category",
        ["Electronics", "Food", "Travel", "Clothing", "Health"]
    )

    foreign_val = 1 if foreign == "Yes" else 0
    mismatch_val = 1 if mismatch == "Yes" else 0

    if st.button("🔍 Analyze Transaction", use_container_width=True):

        payload = {
            "amount": amount,
            "transaction_hour": hour,
            "foreign_transaction": foreign_val,
            "location_mismatch": mismatch_val,
            "device_trust_score": device_score,
            "velocity_last_24h": velocity,
            "cardholder_age": age,
            "merchant_category": category,
        }

        result = None

        with st.spinner("🔄 Running AI risk analysis..."):
            for _ in range(6):
                try:
                    response = requests.post(API_URL, json=payload, timeout=60)
                    if response.status_code == 200:
                        result = response.json()
                        break
                except Exception:
                    pass
                time.sleep(10)

        if result is None:
            st.error("⚠️ Backend temporarily unavailable. Retry in a few seconds.")
            st.stop()

        # ================= HYBRID METRICS =================
        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Final Decision", result["prediction"])
        c2.metric("Risk Score", f"{result['risk_score']}%")
        c3.metric("ML Score (XGB)", f"{result['xgb_score']}%")
        c4.metric("Anomaly Score", f"{result['anomaly_score']}%")

        c5, _ = st.columns(2)
        c5.metric("Rule Score", f"{result['rule_score']}%")

        # ================= GAUGE =================
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=result["risk_score"],
            title={'text': "Fraud Risk Index"},
            gauge={
                'axis': {'range': [0, 100]},
                'steps': [
                    {'range': [0, 40], 'color': '#1f2937'},
                    {'range': [40, 75], 'color': '#374151'},
                    {'range': [75, 100], 'color': '#4b5563'},
                ]
            }
        ))
        st.plotly_chart(fig, use_container_width=True)

        # ================= CONTRIBUTION =================
        contrib_df = pd.DataFrame({
            "Component": ["XGBoost", "Anomaly", "Rules"],
            "Score": [
                result["xgb_score"],
                result["anomaly_score"],
                result["rule_score"]
            ]
        })

        st.plotly_chart(
            px.bar(contrib_df, x="Component", y="Score",
                   title="Fraud Engine Contribution"),
            use_container_width=True
        )

        # ================= REASONS =================
        if result.get("reasons"):
            st.warning("⚠️ AI Risk Drivers:")
            for r in result["reasons"]:
                st.write(f"• {r}")

        # ================= RISK ZONE =================
        if result["risk_score"] > 75:
            st.error("🔴 High Risk Zone")
        elif result["risk_score"] > 40:
            st.warning("🟠 Medium Risk Zone")
        else:
            st.success("🟢 Low Risk Zone")

        # ================= FINAL MESSAGE =================
        if result["prediction"] == "Fraud":
            st.error("🚨 FRAUD ALERT — Immediate Block Recommended")
        else:
            st.success("✅ Transaction Approved — Within Safe Threshold")


# ================= ADMIN =================
else:
    st.subheader("📊 Fraud Risk Command Center")

    auto_refresh = st.toggle("🔄 Auto refresh every 15 sec", value=False)
    if auto_refresh:
        time.sleep(15)
        st.rerun()

    client = MongoClient(MONGO_URI)
    db = client["fraud_detection_db"]
    collection = db["transactions"]
    data = list(collection.find())

    if not data:
        st.warning("No transaction telemetry available yet.")
        st.stop()

    for item in data:
        item["_id"] = str(item["_id"])

    df = pd.DataFrame(data)
    fraud_df = df[df["prediction"] == "Fraud"]

    total = len(df)
    fraud_count = len(fraud_df)
    fraud_rate = round((fraud_count / total) * 100, 2)
    avg_risk = round(df["risk_score"].mean(), 2)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Transactions", total)
    k2.metric("Fraud Cases", fraud_count)
    k3.metric("Fraud Rate", f"{fraud_rate}%")
    k4.metric("Avg Risk", f"{avg_risk}%")

    # ================= HYBRID METRICS =================
    colA, colB, colC = st.columns(3)
    colA.metric("Avg ML Score", round(df["xgb_score"].mean(), 2))
    colB.metric("Avg Anomaly Score", round(df["anomaly_score"].mean(), 2))
    colC.metric("Avg Rule Score", round(df["rule_score"].mean(), 2))

    # ================= VISUALS =================
    row1a, row1b = st.columns(2)

    with row1a:
        st.plotly_chart(px.pie(df, names="prediction",
                               title="Fraud vs Normal"),
                        use_container_width=True)

    with row1b:
        st.plotly_chart(px.histogram(
            df, x="risk_score", color="prediction", nbins=20,
            title="Risk Score Distribution"),
            use_container_width=True)

    # ================= BUSINESS =================
    row2a, row2b = st.columns(2)

    with row2a:
        st.plotly_chart(px.bar(
            df.groupby("merchant_category").size().reset_index(name="count"),
            x="merchant_category", y="count",
            title="Merchant Category Exposure"),
            use_container_width=True)

    with row2b:
        st.plotly_chart(px.line(
            df.groupby("transaction_hour").size().reset_index(name="count"),
            x="transaction_hour", y="count",
            title="Hourly Transaction Velocity"),
            use_container_width=True)

    # ================= HEATMAP =================
    st.plotly_chart(px.density_heatmap(
        df.groupby(["transaction_hour", "prediction"])
        .size().reset_index(name="count"),
        x="transaction_hour",
        y="prediction",
        z="count",
        title="Fraud Heatmap by Hour"),
        use_container_width=True)

    # ================= SCATTER =================
    st.plotly_chart(px.scatter(
        df,
        x="device_trust_score",
        y="risk_score",
        color="prediction",
        title="Device Trust vs Risk Intelligence"),
        use_container_width=True)

    # ================= HYBRID DISTRIBUTION =================
    st.plotly_chart(px.histogram(df, x="xgb_score",
                                 title="ML Score Distribution"),
                    use_container_width=True)

    st.plotly_chart(px.histogram(df, x="anomaly_score",
                                 title="Anomaly Score Distribution"),
                    use_container_width=True)

    # ================= TABLE =================
    sorted_df = df.sort_values(by="risk_score", ascending=False)
    st.dataframe(sorted_df, use_container_width=True)

    # ================= EXPORT =================
    csv = sorted_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Export CSV Report", data=csv,
                       file_name="fraud_report.csv",
                       mime="text/csv")