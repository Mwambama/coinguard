import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

class CoinGuardAgent:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
        self.agent_account = self.w3.eth.account.from_key(os.getenv("AGENT_KEY"))
        
    def analyze_behavior(self, data):
        """
        Logic: If time_spent < 10% of average, flag as speed fraud.
        """
        score = 0
        if data['time_spent'] < (data['avg_time'] * 0.1):
            score += 60  # Immediate fraud threshold
        return score >= 50

    def settle_on_chain(self, payment_id, is_fraud):
        # Build and sign transaction to the 'settle' function in Solidity
        pass # To be implemented in Day 3