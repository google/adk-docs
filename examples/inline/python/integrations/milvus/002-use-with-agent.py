session = await runner.session_service.get_session(
    app_name="milvus_memory_app",
    user_id="user-1",
    session_id="session-1",
)
await memory_service.add_session_to_memory(session)

result = await memory_service.search_memory(
    app_name="milvus_memory_app",
    user_id="user-1",
    query="what did the user say about database preferences?",
)
for memory in result.memories:
    print(memory.content.parts[0].text)