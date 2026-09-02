async for event in self.some_sub_agent.run_async(ctx):
    # Optionally inspect or log the event
    yield event # Pass the event up