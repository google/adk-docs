# Compress workflow context for performance

As an ADK agent runs a workflow it builds up information, including user
instructions, collected data, tool responses, and generated content. As the size
of this in-process data grows, agent processing times typically also increase.
More and more data is sent to the generative AI model used by the agent,
increasing processing time and slowing down responses. The ADK Context
Compaction feature is designed to reduce the size of this in-process data, or
context, by summarizing older parts of the agent workflow event history. 

The Context Compaction feature uses a *sliding window* approach for workflow
event data. When configured, it summarizes data from older events once it
reaches a threshold of a specific number of workflow events.

## Configure context compaction

Add context compaction to your agent workflow by adding an Event Compaction
Configuration setting to the App object of your workflow. As part of the
configuration, you must specify an AI model to perform the event summarization,
as well as set a compaction interval and overlap size, as shown in the following
sample code:

```python
from google.adk.apps.sliding_window_compactor import SlidingWindowCompactor
from google.adk.apps.app import EventsCompactionConfig
from google.adk.models import Gemini

# Define AI model to create summaries.
summarization_llm = Gemini(model="gemini-2.5-flash")
my_compactor = SlidingWindowCompactor(llm=summarization_llm)

app = App(
    name='test',
    root_agent=Mock(spec=BaseAgent),
    events_compaction_config=EventsCompactionConfig(
        compactor=my_compactor,
        compaction_interval=5,  # Trigger compaction every 5 new invocations.
        overlap_size=2          # Include last 2 invocations from the previous window.
    ),
)
```

Once configured, the ADK `Runner` automatically handles the compaction
process in the background after each complete agent invocation event.

### Configuration settings

The configuration setting for this feature control how frequently event data is compressed
and how much data is retained as the agent workflow runs.

*   **`compaction_interval`**: Sets the number of completed events that triggers compaction
    of the prior event data. 
*   **`overlap_size`**: Sets how many of the previously compacted events are included in a
    newly compacted context set.

#### Example

If you set `compaction_interval` to 5 and `overlap_size` to 2, the event data is compressed
upon completion of events 5, 10, 15, and so on. These compression tasks happen as follows:

- Event 5 completes: all 5 events are compressed into a summary
- Event 10 completes: events 4 to 10 are compressed, including the overlap of 2 prior events
- Event 15 completes: events 9 to 15 are compressed, including the overlap of 2 prior events
