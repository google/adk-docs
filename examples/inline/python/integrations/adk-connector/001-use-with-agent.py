import os
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from adk_connectors.telegram import TelegramConnector

# Load environment variables
load_dotenv()

# 1. Define your standard Google ADK Agent
assistant = Agent(
    model='gemini-flash-latest',
    name='my_assistant',
    instruction='You are a helpful assistant.'
)

if __name__ == "__main__":
    # 2. Retrieve your Telegram Bot Token
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    # 3. Bind the connector
    connector = TelegramConnector(
        token=token,
        agent=assistant
    )

    # 4. Start polling
    connector.start()