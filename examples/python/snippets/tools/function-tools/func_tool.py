from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

import yfinance as yf


APP_NAME = "stock_app"
USER_ID = "1234"
SESSION_ID = "session1234"

def get_stock_price(symbol: str):
    """
    Retrieves the current stock price for a given symbol.

    Args:
        symbol (str): The stock symbol (e.g., "AAPL", "GOOG").

    Returns:
        float: The current stock price, or None if an error occurs.
    """
    try:
        stock = yf.Ticker(symbol)
        historical_data = stock.history(period="1d")
        if not historical_data.empty:
            current_price = historical_data['Close'].iloc[-1]
            return current_price
        else:
            return None
    except Exception as e:
        print(f"Error retrieving stock price for {symbol}: {e}")
        return None


stock_price_agent = Agent(
    model='gemini-2.0-flash',
    name='stock_agent',
    instruction= 'You are an agent who retrieves stock prices. If a ticker symbol is provided, fetch the current price. If only a company name is given, first perform a Google search to find the correct ticker symbol before retrieving the stock price. If the provided ticker symbol is invalid or data cannot be retrieved, inform the user that the stock price could not be found.',
    description='This agent specializes in retrieving real-time stock prices. Given a stock ticker symbol (e.g., AAPL, GOOG, MSFT) or the stock name, use the tools and reliable data sources to provide the most up-to-date price.',
    tools=[get_stock_price], # You can add Python functions directly to the tools list; they will be automatically wrapped as FunctionTools.
)


# Session and Runner
session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
runner = Runner(agent=stock_price_agent, app_name=APP_NAME, session_service=session_service)


# Agent Interaction
def call_agent(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)

call_agent("stock price of GOOG")
