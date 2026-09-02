import os

from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

MEMORY_MCP_URL = os.getenv("MEMORY_MCP_URL", "http://localhost:9000")

root_agent = Agent(
    model="gemini-flash-latest",
    name="memory_mcp_agent",
    instruction="Use memory tools to personalize responses.",
    tools=[
        McpToolset(
            connection_params=SseConnectionParams(
                url=f"{MEMORY_MCP_URL.rstrip('/')}/sse",
            ),
            tool_filter=[
                "search_long_term_memory",
                "create_long_term_memories",
                "memory_prompt",
            ],
        ),
    ],
)