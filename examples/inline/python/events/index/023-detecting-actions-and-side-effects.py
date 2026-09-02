if event.actions and event.actions.artifact_delta:
    print(f"  Artifacts saved: {event.actions.artifact_delta}")
    # UI might refresh an artifact list