import streamlit as st
import httpx
import pandas as pd
import os
from dotenv import load_dotenv
from backend.services.web3_client import Web3Client
import plotly.graph_objects as go

# 1. Page Config (Must be first)
st.set_page_config(page_title="CoinGuard AI Dashboard", layout="wide", page_icon="🛡️")

# 2. Load Environment Variables
load_dotenv() 
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
BASE_URL = "http://127.0.0.1:8000"

# Initialize Blockchain Client
blockchain = Web3Client()

def get_vault_balance():
    """Fetches real MNEE balance from the blockchain."""
    try:
        mnee_addr = "0x8ccedbAe4916b79da7F3F612EfB2EB93A2bFD6cF"
        abi = [{"constant":True,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"}]
        token_contract = blockchain.w3.eth.contract(address=mnee_addr, abi=abi)
        # Use your actual contract address from .env
        balance = token_contract.functions.balanceOf(CONTRACT_ADDRESS).call()
        return balance
    except Exception as e:
        return 0

def calculate_total_prevented(df):
    """Calculates sum of MNEE for all transactions marked as FRAUD."""
    if not df.empty and 'verdict' in df.columns:
        # Each demo escrow is 100 MNEE
        fraud_entries = df[df['verdict'] == 'FRAUD']
        return len(fraud_entries) * 100
    return 0

def draw_risk_gauge(score):
    """Creates a professional Green-to-Red Gauge."""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Current Submission Risk Level", 'font': {'size': 24}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "black"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 40], 'color': 'green'},
                {'range': [40, 70], 'color': 'yellow'},
                {'range': [70, 100], 'color': 'red'}],
        }
    ))
    st.plotly_chart(fig, use_container_width=True)

# --- Header ---
st.title("CoinGuard: AI Fraud Detection & Smart Settlement")
st.markdown("### Real-time Monitoring of AI Agent Decisions and Blockchain Transactions")

# 3. Fetch Data for Metrics
try:
    response = httpx.get(f"{BASE_URL}/transactions")
    df_logs = pd.DataFrame(response.json()) if response.status_code == 200 else pd.DataFrame()
except:
    df_logs = pd.DataFrame()

# 4. Metrics Section (4 Columns)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="API Status", value="Connected", delta="Healthy")
with col2:
    # Live vault balance matching Etherscan
    live_bal = get_vault_balance()
    st.metric(label="Vault Balance", value=f"{live_bal} MNEE")
with col3:
    # Counter ticks up by 100 per fraud block
    total_saved = calculate_total_prevented(df_logs)
    st.metric(label="Total Fraud Prevented", value=f"{total_saved} MNEE", delta="Shield Active")
with col4:
    st.metric(label="Network", value="Sepolia Testnet")

st.caption(f"Connected Vault Address: `{CONTRACT_ADDRESS}`")
st.divider()

# --- Risk Gauge Visualization ---
if not df_logs.empty:
    latest_score = df_logs.iloc[-1]['risk_score']
    draw_risk_gauge(latest_score)
else:
    draw_risk_gauge(0)

# --- Live Feed ---
st.subheader("AI Agent Activity")

def get_status():
    try:
        r = httpx.get(f"{BASE_URL}/")
        return r.json().get("message", "Offline")
    except:
        return "Offline"

if st.sidebar.button("Refresh System Data"):
    st.rerun()

st.info(f"System Backend Status: {get_status()}")

# 5. Transaction History (Live Logic)
st.subheader("Transaction History")
if not df_logs.empty:
    if 'transaction_hash' in df_logs.columns:
        df_logs['Etherscan'] = df_logs['transaction_hash'].apply(
            lambda x: f"https://sepolia.etherscan.io/tx/{x}" if x else "N/A"
        )
    
    st.dataframe(
        df_logs,
        column_config={
            "Etherscan": st.column_config.LinkColumn("View on Etherscan"),
            "risk_score": st.column_config.ProgressColumn("Risk Score", min_value=0, max_value=100),
        },
        use_container_width=True,
        hide_index=True
    )
else:
    st.write("No transactions recorded yet. Data will appear after the first settlement.")

st.success("Dashboard is ready to visualize the Scikit-learn model outputs!")