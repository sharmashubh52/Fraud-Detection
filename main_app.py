import time

import streamlit as st
import requests
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="AI Fraud Detection System", page_icon="💳", layout="wide")

# ===== THEME =====
st.markdown("""
<style>
.stApp {
    background-color: #0b1220;
    color: white;
}
div[data-testid="stMetric"] {
    background: #111827;
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

API_URL = os.getenv(
    "API_URL",
    "https://fraud-detection-yrkn.onrender.com"
)
MONGO_URI = os.getenv("MONGO_URI")

st.title("💳 AI Fraud Detection System")
page = st.sidebar.radio("Navigation", ["Customer Transaction", "Admin Dashboard"])

# ================= CUSTOMER =================
if page == "Customer Transaction":
    st.header("🧾 Simulate a Payment")

    col1, col2 = st.columns(2)

    with col1:
        amount = st.number_input("Amount (₹)", min_value=0.0)
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

    if st.button("🔍 Analyze Transaction"):
        payload = {
            "amount": amount,
            "transaction_hour": hour,
            "foreign_transaction": foreign_val,
            "location_mismatch": mismatch_val,
            "device_trust_score": device_score,
            "velocity_last_24h": velocity,
            "cardholder_age": age,
            "merchant_category": category
        }

        st.info("☁️ First request may take up to 60–90 sec because backend is on free cloud.")

        result = None

        with st.spinner("🔄 Analyzing transaction..."):
            for attempt in range(6):
                try:
                    response = requests.post(API_URL, json=payload, timeout=60)

                    if response.status_code == 200:
                        result = response.json()
                        break
                    else:
                        st.error(
                            f"Attempt {attempt+1}: "
                            f"status={response.status_code}\n\n{response.text}"
                    )

                except Exception as e:
                    st.error(f"Attempt {attempt+1}: {str(e)}")

                time.sleep(15)

        if result is None:
            st.error("⚠️ Backend is still failing after retries.")
            st.stop()

        colA, colB = st.columns(2)
        colA.metric("Prediction", result["prediction"])
        colB.metric("Risk Score", f'{result["risk_score"]}%')

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=result["risk_score"],
            title={'text': "Fraud Risk Score"},
            gauge={'axis': {'range': [0, 100]}}
        ))
        st.plotly_chart(fig, use_container_width=True)

        reasons = []
        if amount > 50000:
            reasons.append("High transaction amount")
        if foreign_val == 1:
            reasons.append("Foreign transaction")
        if mismatch_val == 1:
            reasons.append("Location mismatch")
        if device_score < 0.3:
            reasons.append("Low device trust")

        if reasons:
            st.warning("⚠️ Risk Factors: " + ", ".join(reasons))
        if result["prediction"] == "Fraud":
            st.error("🚨 High Risk Transaction — BLOCK")
        else:
            st.success("✅ Transaction Approved")

# ================= ADMIN =================
else:
    st.header("🛡️ Admin Dashboard")

    client = MongoClient(MONGO_URI)
    db = client["fraud_detection_db"]
    collection = db["transactions"]

    data = list(collection.find())

    if len(data) == 0:
        st.warning("No transactions found.")
    else:
        for item in data:
            item["_id"] = str(item["_id"])
    
    df = pd.DataFrame(data)
    fraud_df = df[df["prediction"] == "Fraud"]

    total = len(df)
    fraud_count = len(fraud_df)
    fraud_rate = round((fraud_count / total) * 100, 2)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Transactions", total)
    c2.metric("Fraud Cases", fraud_count)
    c3.metric("Fraud Rate", f"{fraud_rate}%")

    fig_pie = px.pie(df, names="prediction", title="Fraud vs Normal")
    st.plotly_chart(fig_pie, use_container_width=True)

    fig_hist = px.histogram(df, x="risk_score", color="prediction", nbins=20,
                                title="Risk Score Distribution")
    st.plotly_chart(fig_hist, use_container_width=True)
    
    fig_bar = px.bar(
        df.groupby("merchant_category").size().reset_index(name="count"),
        x="merchant_category",
        y="count",
        title="Transactions by Category"
        )
    st.plotly_chart(fig_bar, use_container_width=True)

    fig_line = px.line(
        df.groupby("transaction_hour").size().reset_index(name="count"),
        x="transaction_hour",
        y="count",
        title="Hourly Transaction Trend"
        )
    st.plotly_chart(fig_line, use_container_width=True)

    st.dataframe(df, use_container_width=True)

    # Fraud by hour
    fraud_hour = df[df["prediction"] == "Fraud"]
    fig_fraud_hour = px.bar(
    fraud_hour.groupby("transaction_hour").size().reset_index(name="count"),
    x="transaction_hour",
    y="count",
    title="Fraud Cases by Hour"
    )
    st.plotly_chart(fig_fraud_hour, use_container_width=True)

    # Foreign fraud
    fig_foreign = px.pie(
    df,
    names="foreign_transaction",
    title="Foreign vs Domestic Transactions"
    )
    st.plotly_chart(fig_foreign, use_container_width=True)

    # Device score trend
    fig_device = px.scatter(
    df,
    x="device_trust_score",
    y="risk_score",
    color="prediction",
    title="Device Trust vs Risk Score"
    )
    st.plotly_chart(fig_device, use_container_width=True)
    