import streamlit as st
import requests
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import time

st.set_page_config(page_title="FraudShield AI", page_icon="💳", layout="wide")

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

API_URL = os.getenv("API_URL", "https://fraud-detection-yrkn.onrender.com/check_transaction")
MONGO_URI = os.getenv("MONGO_URI")

st.title("💳 FraudShield AI")
page = st.sidebar.radio("Workspace", ["💳 Transaction Simulator", "📊 Dashboard"])

# ================= CUSTOMER =================
if page == "💳 Transaction Simulator":

    amount = st.number_input("Amount", 0.0)
    hour = st.slider("Hour", 0, 23, 12)
    age = st.number_input("Age", 18, 100, 30)
    foreign = st.selectbox("Foreign", ["No", "Yes"])
    mismatch = st.selectbox("Mismatch", ["No", "Yes"])
    device_score = st.slider("Device Score", 0.0, 1.0, 0.8)
    velocity = st.number_input("Velocity", 0, 50, 1)
    category = st.selectbox("Category", ["Electronics", "Food", "Travel", "Clothing", "Health"])

    if st.button("Analyze"):

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

        for _ in range(5):
            try:
                res = requests.post(API_URL, json=payload, timeout=30)
                if res.status_code == 200:
                    result = res.json()
                    break
            except:
                pass
            time.sleep(5)

        if not result:
            st.error("Backend error")
            st.stop()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Decision", result["prediction"])
        c2.metric("Risk", f"{result['risk_score']}%")
        c3.metric("ML Score", f"{result.get('xgb_score', 0)}%")
        c4.metric("Anomaly", f"{result.get('anomaly_score', 0)}%")
        st.metric("Rule Score", f"{result.get('rule_score', 0)}%")

        # Gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=result["risk_score"],
            title={'text': "Risk"},
            gauge={'axis': {'range': [0, 100]}}
        ))
        st.plotly_chart(fig)

        # Reasons
        if result["reasons"]:
            st.warning(", ".join(result["reasons"]))

# ================= ADMIN =================
else:
    client = MongoClient(MONGO_URI)
    data = list(client["fraud_detection_db"]["transactions"].find())

    for item in data:
        item["_id"] = str(item["_id"])   # 🔥 IMPORTANT FIX

    df = pd.DataFrame(data)

    if df.empty:
        st.warning("No data")
        st.stop()

    st.metric("Total", len(df))
    st.metric("Fraud", len(df[df["prediction"] == "Fraud"]))

    st.plotly_chart(px.pie(df, names="prediction"))

    st.plotly_chart(px.histogram(df, x="risk_score"))

    st.dataframe(df)