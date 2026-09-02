import com.google.adk.apps.App;
import com.google.adk.models.Gemini;
import com.google.adk.summarizer.EventsCompactionConfig;
import com.google.adk.summarizer.LlmEventSummarizer;

// Define the AI model to be used for summarization:
Gemini summarizationLlm = Gemini.builder()
    .model("gemini-flash-latest")
    .build();

// Create the summarizer with the custom model:
LlmEventSummarizer mySummarizer = new LlmEventSummarizer(summarizationLlm);

// Configure the App with the custom summarizer and compaction settings:
App app = App.builder()
    .name("my-agent")
    .rootAgent(rootAgent)
    .eventsCompactionConfig(EventsCompactionConfig.builder()
        .compactionInterval(3)
        .overlapSize(1)
        .summarizer(mySummarizer)
        .build())
    .build();