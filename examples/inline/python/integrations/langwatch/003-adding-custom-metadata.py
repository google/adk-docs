@langwatch.trace(name="ADK Weather Agent")
def run_agent(user_message: str):
    current_trace = langwatch.get_current_trace()
    if current_trace:
        current_trace.update(
            metadata={
                "user_id": "user_123",
                "agent_name": "weather_agent",
                "environment": "production",
            }
        )

    user_msg = types.Content(
        role="user", parts=[types.Part(text=user_message)]
    )
    for event in runner.run(
        user_id="demo-user",
        session_id="demo-session",
        new_message=user_msg,
    ):
        if event.is_final_response():
            return event.content.parts[0].text

    return "No response generated"