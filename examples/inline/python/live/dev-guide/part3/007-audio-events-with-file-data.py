async for event in runner.run_live(
    user_id=user_id,
    session_id=session_id,
    live_request_queue=queue,
    run_config=run_config
):
    if event.content and event.content.parts:
        for part in event.content.parts:
            if part.file_data:
                # Audio aggregated into a file saved in artifacts
                file_uri = part.file_data.file_uri
                mime_type = part.file_data.mime_type

                print(f"Audio file saved: {file_uri} ({mime_type})")
                # Retrieve audio file from artifact service for playback