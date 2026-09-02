import com.google.adk.apps.App;
import com.google.adk.summarizer.EventsCompactionConfig;

App app = App.builder()
    .name("my-agent")
    .rootAgent(rootAgent)
    .eventsCompactionConfig(EventsCompactionConfig.builder()
        .compactionInterval(3)  // Trigger compaction every 3 new invocations.
        .overlapSize(1)         // Include last invocation from the previous window.
        .build())
    .build();