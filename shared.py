# shared.py
import os
from dotenv import load_dotenv
import logging
from typing import Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load .env file
load_dotenv()

# Get the OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY in .env file.")

# Shared LLM configuration used across all agents
llm_config = {
    "config_list": [
        {
            "model": "gpt-3.5-turbo",
            "api_key": OPENAI_API_KEY
        }
    ],
    "temperature": 0.3,
    "timeout": 60
}


# Shared context across agents
class ConversationContext:
    def __init__(self):
        self.account_number = None
        self.loan_id = None

    def update_account_number(self, account_number):
        logger.info(f"Context updated: account_number = {account_number}")
        self.account_number = account_number

    def update_loan_id(self, loan_id):
        logger.info(f"Context updated: loan_id = {loan_id}")
        self.loan_id = loan_id

    def get_account_number(self):
        return self.account_number

    def get_loan_id(self):
        return self.loan_id


# Create shared context
conversation_context = ConversationContext()