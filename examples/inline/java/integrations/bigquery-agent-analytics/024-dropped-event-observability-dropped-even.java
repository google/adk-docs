// Snapshot of {drop_reason: count} since plugin start.
ImmutableMap<String, Long> stats = plugin.getDropStats();
// Example: {queue_full=12, append_error=0, serialization_error=0,
//           after_close=0, shutdown_timeout=0, writer_permit_exhausted=0,
//           writer_create_error=0, late_after_finalize=0}

long totalDropped = stats.values().stream().mapToLong(Long::longValue).sum();