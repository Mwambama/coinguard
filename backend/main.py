from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.services.ai_agent import FraudAgent
from backend.services.web3_client import Web3Client

app = FastAPI()
ai_brain = FraudAgent()
blockchain_body = Web3Client()

# This "Schema" tells FastAPI what to expect from the test script
class SubmissionData(BaseModel):
    payment_id: str
    worker_id: str
    time_spent: int
    avg_time: int
    ip_address: str

@app.get("/")
def home():
    return {"message": "CoinGuard API is live"}

@app.post("/submit-work")
async def handle_submission(submission: SubmissionData):
    try:
        # 1. AI Logic
        # convert the Pydantic object to a dict for our FraudAgent
        risk_score = ai_brain.calculate_risk(submission.dict())
        is_fraud = risk_score >= 50
        
        # 2. Blockchain Logic
        tx_hash = blockchain_body.settle_on_chain(submission.payment_id, is_fraud)
        
        return {
            "status": "Processed",
            "is_fraud": is_fraud,
            "risk_score": risk_score,
            "transaction_hash": tx_hash
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))