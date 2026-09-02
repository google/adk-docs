# ✅ Recommended - Create in async context
async def main():
    queue = LiveRequestQueue()  # Uses existing event loop from async context
    # This is the preferred pattern - ensures queue uses the correct event loop
    # that will run your streaming operations

# ❌ Not recommended - Creates event loop automatically
queue = LiveRequestQueue()  # Works but ADK auto-creates new loop
# This works due to ADK's safety mechanism, but may cause issues with
# loop coordination in complex applications or multi-threaded scenarios