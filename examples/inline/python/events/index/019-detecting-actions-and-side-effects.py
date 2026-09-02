if event.actions and event.actions.state_delta:
    print(f"  State changes: {event.actions.state_delta}")
    # Update local UI or application state if necessary