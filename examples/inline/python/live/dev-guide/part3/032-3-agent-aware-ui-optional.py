current_agent_name = None

async for event in runner.run_live(...):
    # Detect agent transitions
    if event.author and event.author != current_agent_name:
        current_agent_name = event.author
        # Your logic to update UI indicator
        await update_ui_indicator(f"Now: {current_agent_name}")

    # Your event handling logic here
    await handle_event(event)