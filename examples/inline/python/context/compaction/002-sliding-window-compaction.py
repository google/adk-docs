# (Optional) Event-based, sliding window as supplementary setting
compaction_config = EventsCompactionConfig(
    compaction_interval=10,   # Number of turns between standard compactions
    overlap_size=2,           # Number of events to retain as overlapping context