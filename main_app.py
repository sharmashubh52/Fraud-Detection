import streamlit as st
import requests
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import time

# ===== CONFIG =====
st.set_page_config(page_title="FraudShield AI", page_icon="🛡️", layout="wide")

# ===== THEME =====
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0b1220 0%, #111827 100%);
    color: white;
}
div[data-testid="stMetric"] {
    background: rgba(17, 24, 39, 0.9);
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# ===== ENV =====
API_URL = os.getenv("API_URL", "https://fraud-detection-yrkn.onrender.com/check_transaction")
MONGO_URI = os.getenv("MONGO_URI")

st.title("🛡️ FraudShield AI")

page = st.sidebar.radio("Workspace", ["🧾 Transaction Simulator", "📊 Admin Dashboard"])

# =========================================================
# 🧾 CUSTOMER DASHBOARD
# =========================================================
if page == "🧾 Transaction Simulator":

    st.markdown("### Enter Transaction Details")

    col1, col2, col3 = st.columns(3)

    with col1:
        amount = st.number_input("💰 Amount", 0.0)
        hour = st.slider("⏰ Hour", 0, 23, 12)
        age = st.number_input("👤 Age", 18, 100, 30)

    with col2:
        foreign = st.selectbox("🌍 Foreign Transaction", ["No", "Yes"])
        mismatch = st.selectbox("📍 Location Mismatch", ["No", "Yes"])
        velocity = st.number_input("⚡ Velocity (24h)", 0, 50, 1)

    with col3:
        device_score = st.slider("📱 Device Trust Score", 0.0, 1.0, 0.8)
        category = st.selectbox(
            "🏪 Merchant Category",
            ["Electronics", "Food", "Travel", "Clothing", "Health"]
        )

    if st.button("🔍 Analyze Transaction"):

        payload = {
            "amount": amount,
            "transaction_hour": hour,
            "foreign_transaction": 1 if foreign == "Yes" else 0,
            "location_mismatch": 1 if mismatch == "Yes" else 0,
            "device_trust_score": device_score,
            "velocity_last_24h": velocity,
            "cardholder_age": age,
            "merchant_category": category,
        }

        result = None

        with st.spinner("Analyzing transaction..."):
            for _ in range(5):
                try:
                    res = requests.post(API_URL, json=payload, timeout=30)
                    if res.status_code == 200:
                        result = res.json()
                        break
                    else:
                        st.error(f"Backend Error: {res.text}")
                except Exception as e:
                    st.warning(f"Retrying... ({e})")
                time.sleep(2)

        if not result:
            st.error("❌ Backend not responding")
            st.stop()

        # ===== RESULT DISPLAY =====
        st.markdown("## 🧾 Transaction Analysis Result")

        col1, col2 = st.columns([1, 2])

        # LEFT PANEL
        with col1:
            if result["prediction"] == "Fraud":
                st.error("🚨 FRAUD DETECTED")
            else:
                st.success("✅ NORMAL TRANSACTION")

            st.metric("Risk Score", f"{result['risk_score']}%")

        # RIGHT PANEL
        with col2:
            st.markdown("### 📊 Score Breakdown")
            st.progress(result["risk_score"] / 100)
            st.write(f"ML Score: {result['xgb_score']}%")
            st.write(f"Anomaly Score: {result['anomaly_score']}%")
            st.write(f"Rule Score: {result['rule_score']}%")

        # ===== GAUGE =====
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=result["risk_score"],
            title={'text': "Fraud Risk Level"},
            gauge={
                'axis': {'range': [0, 100]},
                'steps': [
                    {'range': [0, 40], 'color': "green"},
                    {'range': [40, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "red"}
                ],
            }
        ))

        st.plotly_chart(fig, use_container_width=True)

        # ===== REASONS =====
        if result["reasons"]:
            st.markdown("### ⚠️ Risk Factors")

            cols = st.columns(len(result["reasons"]))
            for i, reason in enumerate(result["reasons"]):
                cols[i].warning(reason)

# =========================================================
# 📊 ADMIN DASHBOARD
# =========================================================
else:

    st.markdown("### 📊 Fraud Analytics Dashboard")

    client = MongoClient(MONGO_URI)
    data = list(client["fraud_detection_db"]["transactions"].find())

    for item in data:
        item["_id"] = str(item["_id"])

    df = pd.DataFrame(data)

    if df.empty:
        st.warning("No transaction data available")
        st.stop()

    # ===== KPIs =====
    total = len(df)
    fraud_df = df[df["prediction"] == "Fraud"]
    fraud_count = len(fraud_df)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Transactions", total)
    c2.metric("Frauds Detected", fraud_count)
    c3.metric("Fraud Rate", f"{round((fraud_count/total)*100, 2)}%")

    # ===== PIE =====
    st.markdown("### 📊 Fraud Distribution")
    st.plotly_chart(px.pie(df, names="prediction"), use_container_width=True)

    # ===== HISTOGRAM =====
    st.markdown("### 📈 Risk Score Distribution")
    st.plotly_chart(px.histogram(df, x="risk_score", nbins=30), use_container_width=True)

    # ===== CATEGORY FRAUD =====
    st.markdown("### 🏪 Fraud by Category")
    cat_fraud = df[df["prediction"] == "Fraud"]["merchant_category"].value_counts()

    st.plotly_chart(
        px.bar(cat_fraud, title="Fraud Transactions by Category"),
        use_container_width=True
    )

    # ===== HIGH RISK TABLE =====
    st.markdown("### 🚨 High Risk Transactions")
    high_risk = df[df["risk_score"] > 70]

    st.dataframe(high_risk.sort_values(by="risk_score", ascending=False))