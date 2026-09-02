try:
    async for event in runner.run_live(...):
        # ... error handling ...
finally:
    queue.close()  # Cleanup runs whether you break or finish normally