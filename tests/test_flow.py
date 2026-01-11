import httpx
import secrets
import time
import pytest

BASE_URL = "http://127.0.0.1:8000"
# Generate a unique 32-byte ID for this specific test run
SHARED_PAYMENT_ID = "0x" + secrets.token_hex(32)
WORKER_ADDR = "0x79Fa9D791601aA0EAB2da6db50DBFdcb5dCc0DAc"

def test_full_blockchain_flow():
    print(f"\n STARTING FULL FLOW FOR ID: {SHARED_PAYMENT_ID}")

    #  APPROVE (Allow the contract to move your MNEE)
    print("\n1️ Phase 1: Approving MNEE Allowance...")
    # We call a special endpoint we'll add to main.py
    appr_resp = httpx.post(f"{BASE_URL}/approve-tokens", json={"amount": 1000}, timeout=60)
    assert appr_resp.status_code == 200
    print(f" Approved! TX: {appr_resp.json()['tx_hash']}")
    time.sleep(10) # Wait for blockchain to breathe

    # CREATE ESCROW (Lock tokens in the vault)
    print("\n2️ Phase 2: Creating Escrow...")
    escrow_payload = {
        "payment_id": SHARED_PAYMENT_ID,
        "worker_address": WORKER_ADDR,
        "amount": 100,
        "task_id": "HACKATHON-TASK-001"
    }
    escrow_resp = httpx.post(f"{BASE_URL}/create-payment", json=escrow_payload, timeout=60)
    assert escrow_resp.status_code == 200
    print(f" Tokens Locked! TX: {escrow_resp.json()['tx_hash']}")
    time.sleep(15) # Wait for confirmation

    #  SUBMIT WORK & AI SETTLEMENT
    print("\n3️ Phase 3: Submitting Work (Bot Scenario)...")
    work_payload = {
        "payment_id": SHARED_PAYMENT_ID,
        "worker_id": "bot_user_v1",
        "time_spent": 3, # Extreme speed = High risk
        "avg_time": 600
    }
    settle_resp = httpx.post(f"{BASE_URL}/submit-work", json=work_payload, timeout=60)
    data = settle_resp.json()
    
    print(f" AI Risk Score: {data['risk_score']}")
    print(f" Fraud Verdict: {data['is_fraud']}")
    print(f" Settlement TX: {data['transaction_hash']}")

    assert data['is_fraud'] is True
    print("\n🎉 SUCCESS: The AI Agent detected the bot and reversed the payment!")