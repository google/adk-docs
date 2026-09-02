from langfuse import propagate_attributes

SESSION_ID_2 = "demo-session-2"
await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID_2)

with propagate_attributes(
    trace_name="hello-agent-request",
    tags=["google-adk", "cookbook"],
    metadata={"example": "named-trace"},
):
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID_2, new_message=user_msg):
        if event.is_final_response():
            if event.content and event.content.parts:
                print(event.content.parts[0].text)
            elif event.error_message:
                print(f"Agent error: {event.error_message}")