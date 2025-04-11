from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import json

app = FastAPI()

# Load customer data at startup
with open("sample_data.json") as f:
    data = json.load(f)
    CUSTOMERS = data["customers"]

class RequestModel(BaseModel):
    user_text: str = ""
    parameters: dict
    sentiment: str = ""

def find_customer_by_account(account_number):
    return next((c for c in CUSTOMERS if c["account_number"] == account_number), None)

def find_customer_by_loan(loan_id):
    return next((c for c in CUSTOMERS if c["loan_id"] == loan_id), None)

@app.post("/loan_balance")
async def loan_balance_handler(req: RequestModel):
    account = req.parameters.get("account_number")
    customer = find_customer_by_account(account)
    if customer:
        return {"response": f"Loan balance for account {account} is ${customer['loan_balance']}"}
    return JSONResponse(status_code=404, content={"response": "Account not found."})

@app.post("/balance_enquiry")
async def balance_enquiry_handler(req: RequestModel):
    account = req.parameters.get("account_number")
    customer = find_customer_by_account(account)
    if customer:
        return {"response": f"Available account balance for {account} is ${customer['account_balance']}"}
    return JSONResponse(status_code=404, content={"response": "Account not found."})

@app.post("/loan_status")
async def loan_status_handler(req: RequestModel):
    loan_id = req.parameters.get("loan_id")
    customer = find_customer_by_loan(loan_id)
    if customer:
        return {"response": f"Loan ID {loan_id} is currently '{customer['loan_status']}'."}
    return JSONResponse(status_code=404, content={"response": "Loan ID not found."})
