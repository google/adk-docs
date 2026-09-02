if event.actions:
    if event.actions.transfer_to_agent:
        print(f"  Signal: Transfer to {event.actions.transfer_to_agent}")
    if event.actions.escalate:
        print("  Signal: Escalate (terminate loop)")
    if event.actions.skip_summarization:
        print("  Signal: Skip summarization for tool result")