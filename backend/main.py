from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.services.ai_agent import FraudAgent
from backend.services.web3_client import Web3Client

app = FastAPI()
ai_brain = FraudAgent()
blockchain_body = Web3Client()

# Create a simple in-memory log (in a real project, use a database)
transaction_logs = []

# This "Schema" tells FastAPI what to expect from the test script
class SubmissionData(BaseModel):
    payment_id: str
    worker_id: str
    time_spent: int
    avg_time: int
    ip_address: str

class CreatePaymentData(BaseModel):
    payment_id: str
    worker_address: str
    amount: int  # Amount in MNEE (remember decimals!)
    task_id: str  

    # bridge that allows test script to give contract permission to move tokens
    # the approve-tokens endpoint
class ApproveData(BaseModel):
    amount: int

@app.get("/")
def home():
    return {"message": "CoinGuard API is live"}

@app.get("/transactions")
async def get_transactions():
    return transaction_logs

@app.post("/create-payment")
async def create_escrow(data: CreatePaymentData):
    try:
        tx_hash = blockchain_body.create_payment(
            data.payment_id, 
            data.worker_address, 
            data.amount,
            data.task_id
        )
        return {"status": "Success", "tx_hash": tx_hash}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/submit-work")
async def handle_submission(submission: SubmissionData):
    try:
        # 1. AI Logic
        # convert the Pydantic object to a dict for our FraudAgent
        risk_score = ai_brain.calculate_risk(submission.dict())
        is_fraud = risk_score >= 40
        
        # 2. Blockchain Logic
        tx_hash = blockchain_body.settle_on_chain(submission.payment_id, is_fraud)
        
        log_entry = {
            "status": "Success",
            "payment_id": submission.payment_id,
            "worker": submission.worker_id,
            "is_fraud": is_fraud,
            "risk_score": risk_score,
            "transaction_hash": tx_hash,
            "verdict": "FRAUD" if is_fraud else "LEGIT"
        }
        
        transaction_logs.append(log_entry) # Save it!
        return log_entry
        
    except Exception as e:
        # If it fails, it return a structured error so test doesn't crash
        return {
            "status": "Error",
            "error_detail": str(e)
        }

@app.post("/approve-tokens")
async def approve_tokens(data: ApproveData):
    # This calls the method I just updated in web3_client.py
    tx_hash = blockchain_body.approve_mnee(data.amount)
    return {"status": "Success", "tx_hash": tx_hash}