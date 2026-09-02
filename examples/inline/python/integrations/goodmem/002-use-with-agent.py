import os
from google.adk.agents import LlmAgent
from google.adk.apps import App
from goodmem_adk import GoodmemSaveTool, GoodmemFetchTool

save_tool = GoodmemSaveTool(
    base_url=os.getenv("GOODMEM_BASE_URL"),  # e.g. "http://localhost:8080"
    api_key=os.getenv("GOODMEM_API_KEY"),
)
fetch_tool = GoodmemFetchTool(
    base_url=os.getenv("GOODMEM_BASE_URL"),
    api_key=os.getenv("GOODMEM_API_KEY"),
    top_k=5,
)

agent = LlmAgent(
    name="memory_agent",
    model="gemini-flash-latest",
    instruction="You are a helpful assistant with persistent memory.",
    tools=[save_tool, fetch_tool],
)

app = App(name="GoodmemToolsDemo", root_agent=agent)