# All events in this streaming session will have the same invocation_id
async for event in runner.run_live(...):
    print(f"Event ID: {event.id}")              # Unique per event
    print(f"Invocation ID: {event.invocation_id}")  # Same for all events in session