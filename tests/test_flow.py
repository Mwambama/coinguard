import httpx
import time
import pytest

BASE_URL = "http://127.0.0.1:8000"

def test_fraud_scenario():
    print("\n Testing Scenario: BOT DETECTION (Fast Submission)")
    
    # Simulate a bot finishing a 10-minute task in 5 seconds
    payload = {
        "payment_id": "0xABC123...", # Use a real Payment ID from your contract
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
        "payment_id": "0xDEF456...", # Use a different real Payment ID
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