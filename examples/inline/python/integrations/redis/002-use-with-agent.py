from google.adk.agents import Agent
from google.adk.runners import Runner

from adk_redis import (
    RedisLongTermMemoryService,
    RedisLongTermMemoryServiceConfig,
    RedisSessionMemoryService,
    RedisSessionMemoryServiceConfig,
)

# Managed Redis Agent Memory (the default backend).
session_service = RedisSessionMemoryService(
    config=RedisSessionMemoryServiceConfig(
        backend="redis-agent-memory",
        api_base_url="https://your-endpoint.redis.io",
        api_key="...",
        store_id="...",
        default_namespace="my_app",
    ),
)
memory_service = RedisLongTermMemoryService(
    config=RedisLongTermMemoryServiceConfig(
        backend="redis-agent-memory",
        api_base_url="https://your-endpoint.redis.io",
        api_key="...",
        store_id="...",
        default_namespace="my_app",
    ),
)

root_agent = Agent(
    model="gemini-flash-latest",
    name="redis_memory_agent",
    instruction="Use long-term memory to personalize responses.",
)

runner = Runner(
    app_name="redis_memory_app",
    agent=root_agent,
    session_service=session_service,
    memory_service=memory_service,
)