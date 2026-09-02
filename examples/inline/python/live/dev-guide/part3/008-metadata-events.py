async for event in runner.run_live(
    user_id=user_id,
    session_id=session_id,
    live_request_queue=queue,
    run_config=run_config
):
    if event.usage_metadata:
        print(f"Prompt tokens: {event.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {event.usage_metadata.candidates_token_count}")
        print(f"Total tokens: {event.usage_metadata.total_token_count}")

        # Track cumulative usage across the session
        total_tokens += event.usage_metadata.total_token_count or 0