import httpx
import secrets
import pytest
import time

# 1. This ID links all tests together
SHARED_PAYMENT_ID = "0x" + secrets.token_hex(32)
BASE_URL = "http://127.0.0.1:8000"

def test_01_create_escrow():
    """Phase 1: Put money in the vault"""
    payload = {
        "payment_id": SHARED_PAYMENT_ID,
        "worker_address": "0x79Fa9D791601aA0EAB2da6db50DBFdcb5dCc0DAc",
        "amount": 100, # Use a whole number for MNEE
        "task_id": "TASK-101"
    }
    response = httpx.post(f"{BASE_URL}/create-payment", json=payload, timeout=60.0)
    assert response.status_code == 200
    print(f" Escrow Created: {response.json()['tx_hash']}")

def test_02_fraud_scenario():
    """Phase 2: Detect fraud and trigger REFUND settlement"""
    # Notice we use the SAME SHARED_PAYMENT_ID
    payload = {
        "payment_id": SHARED_PAYMENT_ID, 
        "worker_id": "bot_99",
        "time_spent": 5, 
        "avg_time": 600
    }
    
    response = httpx.post(f"{BASE_URL}/submit-work", json=payload, timeout=60.0)
    data = response.json()
    
    assert data['is_fraud'] is True
    print(f"⚖️ Verdict: Fraud. Settlement TX: {data['transaction_hash']}")