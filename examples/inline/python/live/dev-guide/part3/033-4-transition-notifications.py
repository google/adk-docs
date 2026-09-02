async for event in runner.run_live(...):
    # Detect task completion (transition signal)
    if event.content and event.content.parts:
        for part in event.content.parts:
            if (part.function_response and
                part.function_response.name == "task_completed"):
                # Your logic to display transition notification
                await display_notification(
                    f"✓ {event.author} completed. Handing off to next agent..."
                )
                continue

    # Your event handling logic here
    await handle_event(event)