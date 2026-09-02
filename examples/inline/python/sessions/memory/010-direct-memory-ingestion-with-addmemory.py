await memory_service.add_memory(
    app_name="my-app",
    user_id="user-123",
    memories=[
        MemoryEntry(content=Content(parts=[Part(text="The user's favorite color is light blue.")]))
    ],
    custom_metadata={"enable_consolidation": True}
)