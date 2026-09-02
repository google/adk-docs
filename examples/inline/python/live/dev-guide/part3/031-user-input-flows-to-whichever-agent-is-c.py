# ❌ INCORRECT: New queue per agent
for agent in agents:
    new_queue = LiveRequestQueue()  # WRONG!

# ✅ CORRECT: Single queue for entire workflow
queue = LiveRequestQueue()
async for event in runner.run_live(live_request_queue=queue):
    ...