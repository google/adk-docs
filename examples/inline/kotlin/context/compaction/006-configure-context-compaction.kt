import com.google.adk.kt.apps.App
import com.google.adk.kt.summarizer.EventsCompactionConfig

// tokenThreshold and eventRetentionSize must be set together; either alone throws.
// Kotlin also accepts the compactionInterval/overlapSize pair used in the other tabs.
val app =
    App(
        appName = "my-agent",
        rootAgent = rootAgent,
        eventsCompactionConfig =
            EventsCompactionConfig(
                tokenThreshold = 1000, // Compact when the last prompt exceeds 1000 tokens.
                eventRetentionSize = 1, // Keep at least 1 raw event.
            ),
    )