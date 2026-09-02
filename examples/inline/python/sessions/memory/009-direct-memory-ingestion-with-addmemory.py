from google.adk.memory import VertexAiMemoryBankService
from google.adk.memory.memory_entry import MemoryEntry
from google.genai.types import Content, Part

memory_service = VertexAiMemoryBankService(...)

await memory_service.add_memory(
    app_name="my-app",
    user_id="user-123",
    memories=[
        MemoryEntry(content=Content(parts=[Part(text="The user's favorite color is blue.")]))
    ]
)