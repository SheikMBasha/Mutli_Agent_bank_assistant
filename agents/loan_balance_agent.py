# loan_balance_agent.py
from autogen import AssistantAgent
from shared import llm_config, conversation_context
import re
import requests
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def extract_account_number(text):
    match = re.search(r"\b\d{6,}\b", text)
    if match:
        # Update shared context when account number is found
        account_number = match.group(0)
        conversation_context.update_account_number(account_number)
        return account_number
    return None


def check_loan_balance(message_str):
    """Function to check loan balance via API"""
    logger.info(f"check_loan_balance called with: {message_str}")

    # Extract account number from the message
    account_number = extract_account_number(message_str)

    # If no account number in current message, try from context
    if not account_number:
        account_number = conversation_context.get_account_number()
        logger.info(f"Using account number from context: {account_number}")

    # Still no account number, ask for it
    if not account_number:
        return "I need an account number to check your loan balance. Please provide a valid account number."

    logger.info(f"Using account number: {account_number}")

    try:
        # Call the API
        logger.info(f"Calling API endpoint for account: {account_number}")
        response = requests.post(
            "http://localhost:8085/loan_balance",
            json={"parameters": {"account_number": account_number}},
            timeout=10
        )

        # Log response details
        logger.info(f"API response status: {response.status_code}")
        logger.info(f"API response text: {response.text}")

        if response.status_code == 200:
            api_response = response.json()
            result = api_response.get("response")
            logger.info(f"Final result to return: {result}")
            return result
        else:
            logger.error(f"API request failed with status {response.status_code}")
            return "Sorry, I couldn't retrieve your loan balance at this time."

    except Exception as e:
        logger.error(f"Error in check_loan_balance: {str(e)}")
        return "Sorry, there was an error connecting to the banking system."


# Create a custom reply function
def custom_reply(agent, messages=None, sender=None, config=None):
    """Custom function for handling loan balance inquiries"""
    if not messages:
        return False, None

    last_message = messages[-1]
    content = last_message.get("content", "") if isinstance(last_message, dict) else str(last_message)

    # Check if this is a loan balance inquiry message
    loan_keywords = ["loan balance", "loan amount", "how much loan"]
    is_loan_request = any(keyword in content.lower() for keyword in loan_keywords) or "@LoanBalanceAgent" in content

    if is_loan_request:
        logger.info(f"Loan balance inquiry detected: {content}")
        result = check_loan_balance(content)
        logger.info(f"Returning API result: {result}")
        return True, result

    return False, None


# Create the loan balance agent
loan_balance_agent = AssistantAgent(
    name="LoanBalanceAgent",
    llm_config=llm_config,
    system_message="""
You are the LoanBalanceAgent, specializing in checking loan balances.
You can retrieve customer loan balances when provided with an account number.
"""
)

# Register our custom handler
loan_balance_agent.register_reply(
    trigger=lambda x: True,  # We'll do our own checking in the function
    reply_func=custom_reply
)

logger.info("LoanBalanceAgent initialized with custom reply handler for direct API access")