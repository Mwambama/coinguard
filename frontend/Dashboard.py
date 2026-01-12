import streamlit as st
import httpx
import pandas as pd
import time

# Page Config
st.set_page_config(page_title="CoinGuard AI Dashboard", layout="wide", page_icon="🛡️")

st.title("CoinGuard: AI Fraud Detection & Smart Settlement")
st.markdown("### Real-time Monitoring of AI Agent Decisions and Blockchain Transactions")

# --- System Overview Metrics ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="API Status", value="Connected", delta="Healthy")
with col2:
    st.metric(label="Network", value="Sepolia Testnet")
with col3:
    # Use your actual contract address from .env
    st.metric(label="Vault Balance", value="1,000 MNEE")

st.divider()

# --- Live Decision Feed ---
st.subheader("AI Agent Activity")

# Logic to pull from FastAPI backend
def get_status():
    try:
        response = httpx.get("http://127.0.0.1:8000/")
        return response.json().get("message", "Offline")
    except:
        return "Offline"

if st.sidebar.button("Refresh System Data"):
    st.rerun()

# Simulation & Visualization 
st.info(f"System Backend Status: {get_status()}")

# Example Table of recent activity
st.subheader("Transaction History")
# In a full project, these would be fetched from a database or blockchain events
demo_data = {
    "Payment ID": ["0x719f...", "0x1989..."],
    "Worker": ["bot_user_v1", "human_01"],
    "AI Risk Score": [98.0, 12.5],
    "Verdict": [" FRAUD", "LEGIT"],
    "Action": ["Refunded", "Released"],
    "Etherscan": ["[Link](https://sepolia.etherscan.io/)", "[Link](https://sepolia.etherscan.io/)"]
}
df = pd.DataFrame(demo_data)
st.table(df)

st.success("Dashboard is ready to visualize the Scikit-learn model outputs!")