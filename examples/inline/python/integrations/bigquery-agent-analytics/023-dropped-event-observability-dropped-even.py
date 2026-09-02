# Snapshot of {drop_reason: count} since plugin start.
stats = plugin.get_drop_stats()
# Example: {"queue_full": 12, "retry_exhausted": 0, ...}

total_dropped = sum(stats.values())