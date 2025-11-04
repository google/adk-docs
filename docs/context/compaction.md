# Compress agent context for performance

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.16.0</span>
</div>

As an ADK agent runs it collects *context* information, including user
instructions, retrieved data, tool responses, and generated content. As the size
of this context data grows, agent processing times typically also increase.
More and more data is sent to the generative AI model used by the agent,
increasing processing time and slowing down responses. The ADK Context
Compaction feature is designed to reduce the size of context as an agent
is running by summarizing older parts of the agent workflow event history. 

The Context Compaction feature uses a *sliding window* approach for collecting
and summarizing agent workflow event data within a
[Session](/adk-docs/sessions/session/). When you configure this feature in your
agent, it summarizes data from older events once it reaches a threshold of a
specific number of workflow events, or invocations, with the current Session.

## Configure context compaction

Add context compaction to your agent workflow by adding an Events Compaction
Configuration setting to the App object of your workflow. As part of the
configuration, you must specify a compaction interval and overlap size, as shown
in the following sample code:

```python
from google.adk.apps.app import App
from google.adk.apps.app import EventsCompactionConfig

app = App(
    name='my-agent',
    root_agent=root_agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=3,  # Trigger compaction every 3 new invocations.
        overlap_size=1          # Include last invocation from the previous window.
    ),
)
```

Once configured, the ADK `Runner` handles the compaction process in the
background each time the session reaches the interval.

## Example of context compaction

If you set `compaction_interval` to 3 and `overlap_size` to 1, the event data is
compressed upon completion of events 3, 6, 9, and so on. The overlap setting
increases size of the second summary compression, and each summary afterwards,
as shown in Figure 1. 

![Context compaction example illustration](/adk-docs/assets/context-compaction.svg)
**Figure 1.** Ilustration of event compaction configuration with a interval of 3
and overlap of 1.

With this example configuration, the context compression tasks happen as follows:

1.  **Event 3 completes**: All 3 events are compressed into a summary
1.  **Event 6 completes**: Events 3 to 6 are compressed, including the overlap
    of 1 prior event
1.  **Event 9 completes**: Events 6 to 9 are compressed, including the overlap
    of 1 prior event

## Configuration settings

The configuration settings for this feature control how frequently event data is compressed
and how much data is retained as the agent workflow runs. Optionally, you can configure
a compactor object 

*   **`compaction_interval`**: Set the number of completed events that triggers compaction
    of the prior event data. 
*   **`overlap_size`**: Set how many of the previously compacted events are included in a
    newly compacted context set.
*   **`compactor`**: (Optional) Define a compactor object including a specific AI model
    to use for summarization. For more information, see 
    [Define a compactor](#define-compactor).    

### Define a Compactor {#define-compactor}

You can define a Compactor object using the `SlidingWindowCompactor` class to
customize the operation of context compression. The following code example
demonstrates how to define a compactor:

```python
from google.adk.apps.app import App
from google.adk.apps.app import EventsCompactionConfig
from google.adk.models import Gemini
from google.adk.apps.sliding_window_compactor import SlidingWindowCompactor

# Define a compactor using a specific AI model:
summarization_llm = Gemini(model="gemini-2.5-flash")
my_compactor = SlidingWindowCompactor(llm=summarization_llm)

app = App(
    name='my-agent',
    root_agent=root_agent,
    events_compaction_config=EventsCompactionConfig(
        compactor=my_compactor,
        compaction_interval=3, overlap_size=1
    ),
)    
```

You can further refine the operation of the `SlidingWindowCompactor` by
by modifying its summarizer class `LlmEventSummarizer` including changing
the `prompt_template` setting of that class. For more details, see the
[`LlmEventSummarizer` code](https://github.com/google/adk-python/blob/main/src/google/adk/apps/llm_event_summarizer.py#L60).