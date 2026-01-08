# import os
# from web3 import Web3
# from dotenv import load_dotenv

# load_dotenv()

# class CoinGuardAgent:
#     def __init__(self):
#         self.w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
#         self.agent_account = self.w3.eth.account.from_key(os.getenv("AGENT_KEY"))
        
#     def analyze_behavior(self, data):
#         """
#         Logic: If time_spent < 10% of average, flag as speed fraud.
#         """
#         score = 0
#         if data['time_spent'] < (data['avg_time'] * 0.1):
#             score += 60  # Immediate fraud threshold
#         return score >= 50

#     def settle_on_chain(self, payment_id, is_fraud):
#         # Build and sign transaction to the 'settle' function in Solidity
#         pass # To be implemented in Day 3

import numpy as np

class FraudAgent:
    def __init__(self):
        # assign weights to different behaviors
        self.w_speed = 0.4    # How fast they finished
        self.w_bot = 0.6      # How 'exact' their timing is (bot signal)

    def calculate_risk(self, submission_data):
        """
        Input: {'time_spent': int, 'avg_time': int}
        Output: float (0.0 to 100.0)
        """
        score = 0
        
        # 1. Velocity Anomaly: Completed in < 15% of average time
        if submission_data['time_spent'] < (submission_data['avg_time'] * 0.15):
            score += 100 * self.w_speed
            
        # 2. Robotic Timing: Humans are messy. Bots are consistent.
        # If the task took EXACTLY 30s, 60s, or 120s, it's a huge bot flag.
        if submission_data['time_spent'] in [30, 60, 120, 300]:
            score += 100 * self.w_bot
            
        return score