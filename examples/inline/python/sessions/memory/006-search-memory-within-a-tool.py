from google.adk.tools import ToolContext

async def search_past_conversations(
    query: str, tool_context: ToolContext
) -> dict:
    response = await tool_context.search_memory(query)
    return {
        "results": [
            part.text
            for entry in response.memories
            for part in (entry.content.parts or [])
            if part.text
        ]
    }