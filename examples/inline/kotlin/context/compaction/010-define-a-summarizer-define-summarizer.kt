import com.google.adk.kt.apps.App
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.summarizer.EventsCompactionConfig
import com.google.adk.kt.summarizer.LlmEventSummarizer

// Define the AI model to be used for summarization:
val summarizationLlm = Gemini(name = "gemini-flash-latest")

// Create the summarizer with the custom model:
val mySummarizer = LlmEventSummarizer(model = summarizationLlm)

// Configure the App with the custom summarizer and compaction settings:
val app =
    App(
        appName = "my-agent",
        rootAgent = rootAgent,
        eventsCompactionConfig =
            EventsCompactionConfig(
                compactionInterval = 3,
                overlapSize = 1,
                summarizer = mySummarizer,
            ),
    )