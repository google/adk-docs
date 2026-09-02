import os
from google.adk.agents import LlmAgent
from google.adk.apps import App
from goodmem_adk import GoodmemPlugin

plugin = GoodmemPlugin(
    base_url=os.getenv("GOODMEM_BASE_URL"),  # e.g. "http://localhost:8080"
    api_key=os.getenv("GOODMEM_API_KEY"),
    top_k=5,  # Number of memories to retrieve per turn
)

agent = LlmAgent(
    name="memory_agent",
    model="gemini-flash-latest",
    instruction="You are a helpful assistant with persistent memory.",
)

app = App(name="GoodmemPluginDemo", root_agent=agent, plugins=[plugin])