retry_count = 0
max_retries = 3

async for event in runner.run_live(...):
    if event.error_code == "RESOURCE_EXHAUSTED":
        retry_count += 1
        if retry_count > max_retries:
            logger.error("Max retries exceeded")
            break  # Give up after multiple failures

        # Wait and retry
        await asyncio.sleep(2 ** retry_count)  # Exponential backoff
        continue  # Keep listening - rate limit may clear

    # Reset counter on successful event
    retry_count = 0