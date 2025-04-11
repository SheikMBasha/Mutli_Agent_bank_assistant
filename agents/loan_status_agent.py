# loan_status_agent.py
from autogen import AssistantAgent
from shared import llm_config, conversation_context
import re
import requests
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def extract_loan_id(text):
    match = re.search(r"\b(LN\d+)\b", text)
    if match:
        # Update shared context when loan ID is found
        loan_id = match.group(0)
        conversation_context.update_loan_id(loan_id)
        return loan_id
    return None


def extract_account_number(text):
    match = re.search(r"\b\d{6,}\b", text)
    if match:
        # Update shared context when account number is found
        account_number = match.group(0)
        conversation_context.update_account_number(account_number)
        return account_number
    return None


def check_loan_status(message_str):
    """Function to check loan status via API"""
    logger.info(f"check_loan_status called with: {message_str}")

    # Extract loan ID from the message
    loan_id = extract_loan_id(message_str)

    # If no loan ID in current message, try from context
    if not loan_id:
        loan_id = conversation_context.get_loan_id()
        logger.info(f"Using loan ID from context: {loan_id}")

    # Still no loan ID, try to find loan ID using account number
    if not loan_id:
        # Try to get account number
        account_number = extract_account_number(message_str)
        if not account_number:
            account_number = conversation_context.get_account_number()
            logger.info(f"Using account number from context: {account_number}")

        # If we have account number, we could try to get loan ID from it
        # This would need to be implemented in your API, getting loan ID from account number
        if account_number:
            logger.info(f"Attempting to find loan ID for account: {account_number}")
            # For now, hardcode the mapping based on your sample_data.json
            if account_number == "123456789":
                loan_id = "LN1001"
                conversation_context.update_loan_id(loan_id)
                logger.info(f"Found loan ID for account: {loan_id}")
            elif account_number == "987654321":
                loan_id = "LN1002"
                conversation_context.update_loan_id(loan_id)
                logger.info(f"Found loan ID for account: {loan_id}")

    # Still no loan ID, ask for it
    if not loan_id:
        return "I need a loan ID (format: LNxxxx) to check your loan status. Please provide a valid loan ID."

    logger.info(f"Using loan ID: {loan_id}")

    try:
        # Call the API
        logger.info(f"Calling API endpoint for loan ID: {loan_id}")
        response = requests.post(
            "http://localhost:8085/loan_status",
            json={"parameters": {"loan_id": loan_id}},
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
            return "Sorry, I couldn't retrieve your loan status at this time."

    except Exception as e:
        logger.error(f"Error in check_loan_status: {str(e)}")
        return "Sorry, there was an error connecting to the banking system."


# Create a custom reply function
def custom_reply(agent, messages=None, sender=None, config=None):
    """Custom function for handling loan status inquiries"""
    if not messages:
        return False, None

    # Get the last message
    last_message = messages[-1]
    content = last_message.get("content", "") if isinstance(last_message, dict) else str(last_message)

    # Check if this is a loan status inquiry message or contains a loan ID
    status_keywords = ["loan status", "approved", "status of loan", "loan application", "status"]
    is_status_request = any(keyword in content.lower() for keyword in status_keywords) or "@LoanStatusAgent" in content
    has_loan_id = extract_loan_id(content) is not None

    if is_status_request or has_loan_id:
        logger.info(f"Loan status inquiry detected: {content}")
        result = check_loan_status(content)
        logger.info(f"Returning API result: {result}")
        return True, result

    return False, None


# Create the loan status agent
loan_status_agent = AssistantAgent(
    name="LoanStatusAgent",
    llm_config=llm_config,
    system_message="""
You are the LoanStatusAgent, specializing in checking loan application status.
You can retrieve loan status information when provided with a loan ID (format: LNxxxx).
If you already know the account number, you can sometimes determine the loan ID.
"""
)

# Register our custom handler
loan_status_agent.register_reply(
    trigger=lambda x: True,  # We'll do our own checking in the function
    reply_func=custom_reply
)

logger.info("LoanStatusAgent initialized with custom reply handler for direct API access")