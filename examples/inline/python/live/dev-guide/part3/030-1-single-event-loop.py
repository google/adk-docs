# ✅ CORRECT: One loop handles all agents
async for event in runner.run_live(...):
    # Your event handling logic here
    await handle_event(event)  # Works for Agent1, Agent2, Agent3...

# ❌ INCORRECT: Don't break the loop or create multiple loops
for agent in agents:
    async for event in runner.run_live(...):  # WRONG!
        ...