# main.py
from autogen import UserProxyAgent, GroupChat, GroupChatManager
from agents.router_agent import router_agent
from agents.loan_balance_agent import loan_balance_agent
from agents.balance_enquiry_agent import balance_enquiry_agent
from agents.loan_status_agent import loan_status_agent
from shared import llm_config

# Define the user-facing proxy agent
user_proxy = UserProxyAgent(
    name="user",
    human_input_mode="ALWAYS",  # Set to ALWAYS for interactive testing
    code_execution_config=False,
    max_consecutive_auto_reply=0
)

# Create a group chat of all agents
groupchat = GroupChat(
    agents=[
        user_proxy,
        router_agent,
        loan_balance_agent,
        balance_enquiry_agent,
        loan_status_agent
    ],
    messages=[],
    max_round=10
)

# GroupChatManager orchestrates who speaks when
manager = GroupChatManager(
    groupchat=groupchat,
    llm_config=llm_config,
    code_execution_config={"use_docker": False}
)

if __name__ == "__main__":
    mode = input("Run full assistant? (y/n): ").strip().lower()

    if mode == "y":
        print("💬 Multi-Agent Banking Assistant (AutoGen)")
        user_proxy.initiate_chat(manager)
    else:
        print("💬 Direct Agent Test Mode")
        test_message = input("Enter test message: ")
        user_proxy.initiate_chat(
            balance_enquiry_agent,  # or loan_balance_agent, loan_status_agent
            message=test_message,
            summary_method="last_msg"
        )