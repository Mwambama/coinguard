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
import joblib  #for saving/loading
import os

class FraudAgent:
    def __init__(self):
        self.model_path = "backend/services/fraud_model.joblib"
        self.model = None
        
        # Check if a saved model already exists
        if os.path.exists(self.model_path):
            print("AI Agent: Loading existing model from disk...")
            self.model = joblib.load(self.model_path) # Load instantly
        else:
            print("AI Agent: No model found. Training new model...")
            self._train_and_save_model()

    def _train_and_save_model(self):
        """Trains the initial model and persists it to a file."""
        # Synthetic Training Data
        data = [
            [600, 600, 0, 0], [450, 600, 0, 0], # Human : there is normal than fast human
            [1, 600, 1, 1],   [5, 600, 1, 1]    # Bot
        ]
        df = pd.DataFrame(data, columns=['time_spent', 'avg_time', 'suspicious_ip', 'target'])
        X = df[['time_spent', 'avg_time', 'suspicious_ip']]
        y = df['target']
        
        self.model = RandomForestClassifier(n_estimators=100)
        self.model.fit(X, y)
        
        # Save the model to a file so it persists
        joblib.dump(self.model, self.model_path)
        print(f"AI Agent: Model saved to {self.model_path}")

    def calculate_risk(self, data):
        """Uses the persisted ML model to predict fraud."""
        is_suspicious_ip = 1 if data.get('ip_address') == '1.2.3.4' else 0
        features = np.array([[
            data.get('time_spent', 0),
            data.get('avg_time', 600),
            is_suspicious_ip
        ]])
        
        risk_prob = self.model.predict_proba(features)[0][1]
        return float(risk_prob * 100)