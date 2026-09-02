# Example: Comprehensive tool implementation showing common InvocationContext patterns
def my_tool(context: InvocationContext, query: str):
    # Access user identity
    user_id = context.session.user_id

    # Check if this is the user's first message
    event_count = len(context.session.events)
    if event_count == 0:
        return "Welcome! This is your first message."

    # Access conversation history
    recent_events = context.session.events[-5:]  # Last 5 events

    # Access persistent session state
    # Session state persists across invocations (not just this streaming session)
    user_preferences = context.session.state.get('user_preferences', {})

    # Update session state (will be persisted)
    context.session.state['last_query_time'] = datetime.now().isoformat()

    # Access services for persistence
    if context.artifact_service:
        # Store large files/audio
        await context.artifact_service.save_artifact(
            app_name=context.session.app_name,
            user_id=context.session.user_id,
            session_id=context.session.id,
            filename="result.bin",
            artifact=types.Part(inline_data=types.Blob(mime_type="application/octet-stream", data=data)),
        )

    # Process the query with context
    result = process_query(query, context=recent_events, preferences=user_preferences)

    # Terminate conversation in specific scenarios
    if result.get('error'):
        # Processing error - stop conversation
        context.end_invocation = True

    return result