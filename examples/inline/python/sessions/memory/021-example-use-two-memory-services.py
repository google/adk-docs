from google.adk.agents import Agent
from google.adk.memory import InMemoryMemoryService
from google.adk.tools import ToolContext

# Second memory service for docs lookup; could be any BaseMemoryService.
docs_memory = InMemoryMemoryService()


async def search_all_memory(query: str, tool_context: ToolContext) -> dict:
    """Search both the conversational memory and the docs corpus."""
    conversational = await tool_context.search_memory(query)
    docs = await docs_memory.search_memory(
        app_name="docs", user_id="shared", query=query
    )
    return {
        "from_conversations": [
            part.text
            for entry in conversational.memories
            for part in (entry.content.parts or [])
            if part.text
        ],
        "from_docs": [
            part.text
            for entry in docs.memories
            for part in (entry.content.parts or [])
            if part.text
        ],
    }


agent = Agent(
    model="gemini-flash-latest",
    name="multi_memory_agent",
    instruction=(
        "Answer questions using both your conversation history and the "
        "docs knowledge base. Use the search_all_memory tool."
    ),
    tools=[search_all_memory],
)