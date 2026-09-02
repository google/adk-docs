import asyncio

async def export_loop(plugin):
    last = {k: 0 for k in (
        "queue_full", "arrow_prep_failed",
        "retry_exhausted", "non_retryable", "unexpected_error",
    )}
    while True:
        current = plugin.get_drop_stats()
        for reason, count in current.items():
            delta = count - last.get(reason, 0)
            if delta:
                # e.g. metric_client.write_point(
                #         metric="bqaa_dropped_events",
                #         labels={"reason": reason}, value=delta)
                ...
        last = current
        await asyncio.sleep(60)