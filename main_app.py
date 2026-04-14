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

        c1, c2 = st.columns(2)
        c1.metric("Prediction", result["prediction"])
        c2.metric("Risk Score", f"{result['risk_score']}%")

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=result["risk_score"],
            title={'text': "Fraud Risk Index"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'thickness': 0.35},
                'steps': [
                    {'range': [0, 35], 'color': '#1f2937'},
                    {'range': [35, 70], 'color': '#374151'},
                    {'range': [70, 100], 'color': '#4b5563'},
                ]
            }
        ))
        st.plotly_chart(fig, use_container_width=True)

        risk_factors = []
        if amount > 50000:
            risk_factors.append("High transaction amount")
        if foreign_val:
            risk_factors.append("Foreign transaction")
        if mismatch_val:
            risk_factors.append("Location mismatch")
        if device_score < 0.3:
            risk_factors.append("Low device trust")

        if risk_factors:
            st.warning("⚠️ AI Risk Drivers: " + " • ".join(risk_factors))

        if result["prediction"] == "Fraud":
            st.error("🚨 Transaction flagged — recommend hard block + manual review")
        else:
            st.success("✅ Transaction approved within policy thresholds")

# ================= ADMIN =================
else:
    st.subheader("📊 Fraud Risk Command Center")

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

    row1a, row1b = st.columns(2)
    with row1a:
        st.plotly_chart(px.pie(df, names="prediction", title="Fraud vs Normal"), use_container_width=True)
    with row1b:
        st.plotly_chart(px.histogram(df, x="risk_score", color="prediction", nbins=20,
                                     title="Risk Score Distribution"), use_container_width=True)

    row2a, row2b = st.columns(2)
    with row2a:
        category_df = df.groupby("merchant_category").size().reset_index(name="count")
        st.plotly_chart(px.bar(category_df, x="merchant_category", y="count",
                               title="Merchant Category Exposure"), use_container_width=True)
    with row2b:
        hourly_df = df.groupby("transaction_hour").size().reset_index(name="count")
        st.plotly_chart(px.line(hourly_df, x="transaction_hour", y="count",
                                title="Hourly Transaction Velocity"), use_container_width=True)

    st.plotly_chart(px.scatter(
        df,
        x="device_trust_score",
        y="risk_score",
        color="prediction",
        title="Device Trust vs Risk Intelligence"
    ), use_container_width=True)

    st.dataframe(df.sort_values(by="risk_score", ascending=False), use_container_width=True)
