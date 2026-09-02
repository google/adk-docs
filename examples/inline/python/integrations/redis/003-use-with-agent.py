from google.adk.agents import Agent

from adk_redis import (
    CreateMemoryTool,
    DeleteMemoryTool,
    MemoryPromptTool,
    MemoryToolConfig,
    SearchMemoryTool,
    UpdateMemoryTool,
)

config = MemoryToolConfig(
    backend="redis-agent-memory",
    api_base_url="https://your-endpoint.redis.io",
    api_key="...",
    store_id="...",
    default_namespace="my_app",
)

root_agent = Agent(
    model="gemini-flash-latest",
    name="redis_memory_tools_agent",
    instruction="Search memory before answering. Store important facts.",
    tools=[
        SearchMemoryTool(config=config),
        CreateMemoryTool(config=config),
        UpdateMemoryTool(config=config),
        DeleteMemoryTool(config=config),
        MemoryPromptTool(config=config),
    ],
)