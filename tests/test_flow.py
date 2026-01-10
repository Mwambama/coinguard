import httpx
import time
import pytest
import secrets # To generate unique IDs | test_01_create_escrow

#  for the first method: test_01_create_escrow
# Generate a fresh 32-byte ID for this specific test run
SHARED_PAYMENT_ID = "0x" + secrets.token_hex(32)
WORKER_ADDR = "0x79Fa9D791601aA0EAB2da6db50DBFdcb5dCc0DAc" # Using MetaMask address

BASE_URL = "http://127.0.0.1:8000"


# def test_01_create_escrow():
#     print(f"\n💰 Phase 1: Creating Escrow for {SHARED_PAYMENT_ID}")
#     # In a real app, you'd have an endpoint for this
#     # For now, let's assume we call a 'setup' endpoint or use the client directly
#     payload = {
#         "payment_id": SHARED_PAYMENT_ID,
#         "worker_address": WORKER_ADDR,
#         "amount": 0.001 
#     }
#     # (Assuming you add a POST /create-payment endpoint in main.py)
#     response = httpx.post(f"{BASE_URL}/create-payment", json=payload, timeout=60.0)
#     assert response.status_code == 200
#     print(f"Escrow Hash: {response.json()['tx_hash']}")

def test_fraud_scenario():
    print("\n Testing Scenario: BOT DETECTION (Fast Submission)")
    
    # Simulate a bot finishing a 10-minute task in 5 seconds
    payload = {
        "payment_id": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef", # Using real Payment ID from contract
        "worker_id": "bot_user_99",
        "time_spent": 5, 
        "avg_time": 600, # 10 minutes in seconds
        "ip_address": "192.168.1.1"
    }
    
    response = httpx.post(f"{BASE_URL}/submit-work", json=payload, timeout=30.0)
    data = response.json()
    
    print(f"Result: {data['status']}")
    print(f"Risk Score: {data['risk_score']}")
    print(f"Blockchain TX: {data['transaction_hash']}")
    
    assert data['is_fraud'] is True
    assert "transaction_hash" in data

def test_legitimate_scenario():
    print("\n Testing Scenario: HUMAN DETECTION (Normal Speed)")
    
    # Simulate a human finishing a 10-minute task in 8 minutes
    payload = {
        "payment_id": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef", # Use a different real Payment ID
        "worker_id": "human_worker_01",
        "time_spent": 480, # 8 minutes
        "avg_time": 600,
        "ip_address": "192.168.1.2"
    }
    
    response = httpx.post(f"{BASE_URL}/submit-work", json=payload, timeout=30.0)
    data = response.json()
    
    print(f"Result: {data['status']}")
    print(f"Risk Score: {data['risk_score']}")
    print(f"Blockchain TX: {data['transaction_hash']}")
    
    assert data['is_fraud'] is False


   