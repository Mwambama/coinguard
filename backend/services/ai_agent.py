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


# this so far, I am implementing 
# import numpy as np

# class FraudAgent:
#     def __init__(self):
#         # assign weights to different behaviors
#         self.w_speed = 0.4    # How fast they finished
#         self.w_bot = 0.6      # How 'exact' their timing is (bot signal)

#     def calculate_risk(self, submission_data):
#         """
#         Input: {'time_spent': int, 'avg_time': int}
#         Output: float (0.0 to 100.0)
#         """
#         score = 0
        
#         # 1. Velocity Anomaly: Completed in < 15% of average time
#         if submission_data['time_spent'] < (submission_data['avg_time'] * 0.15):
#             score += 100 * self.w_speed
            
#         # 2. Robotic Timing: Humans are messy. Bots are consistent.
#         # If the task took EXACTLY 30s, 60s, or 120s, it's a huge bot flag.
#         if submission_data['time_spent'] in [30, 60, 120, 300]:
#             score += 100 * self.w_bot
            
#         return score



import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import os

class FraudAgent:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100)
        self._train_initial_model() # Give the AI a starting "brain"

    def _train_initial_model(self):
        """Generates synthetic data to train the model for the demo."""
        # Features: [time_spent, avg_time, is_suspicious_ip]
        # 0 = Human, 1 = Bot
        data = [
            [600, 600, 0, 0],  # Normal Human
            [450, 600, 0, 0],  # Fast Human
            [5, 600, 1, 1],    # Obvious Bot
            [10, 600, 0, 1],   # Fast Bot
            [550, 600, 1, 0],  # Human on VPN (maybe)
            [1, 600, 1, 1]     # Extreme Bot
        ]
        df = pd.DataFrame(data, columns=['time_spent', 'avg_time', 'suspicious_ip', 'target'])
        
        X = df[['time_spent', 'avg_time', 'suspicious_ip']]
        y = df['target']
        self.model.fit(X, y)
        print(" AI Agent: Scikit-learn model trained and ready.")

    def calculate_risk(self, data):
        """Uses the ML model to predict fraud probability."""
        # Prepares the features from the incoming request
        is_suspicious_ip = 1 if data.get('ip_address') == '1.2.3.4' else 0
        features = np.array([[
            data.get('time_spent', 0),
            data.get('avg_time', 600),
            is_suspicious_ip
        ]])
        
        # predict_proba returns [prob_human, prob_bot]
        # We take the prob_bot (index 1) and turn it into a 0-100 score
        risk_prob = self.model.predict_proba(features)[0][1]
        risk_score = float(risk_prob * 100)
        
        print(f" AI Inference: Risk Score {risk_score}%")
        return risk_score