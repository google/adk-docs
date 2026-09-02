from google.adk.agents import Agent
from google.adk.tools import preload_memory

agent = Agent(
    model=MODEL_ID,
    name='weather_sentiment_agent',
    instruction="...",
    tools=[preload_memory]
)