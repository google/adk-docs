import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

agent = Agent(
    name="assistant",
    model=LiteLlm(
        model=os.getenv("RESPAN_MODEL", "openai/gpt-5-mini"),
        api_key=os.environ["RESPAN_API_KEY"],
        api_base=os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api"),
    ),
    instruction="You are a concise assistant.",
)