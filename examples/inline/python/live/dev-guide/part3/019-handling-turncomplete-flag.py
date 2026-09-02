async for event in runner.run_live(...):
    if event.turn_complete:
        # Your logic to update UI to show "ready for input" state
        enable_user_input()
        # Your logic to hide typing indicator
        hide_typing_indicator()

        # Your logic to mark conversation boundary in logs
        log_turn_boundary()