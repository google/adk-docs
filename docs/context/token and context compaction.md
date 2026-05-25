# Compress agent context for performance

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.16.0</span><span class="lst-java">Java v0.2.0</span><span class="lst-typescript">TypeScript v0.6.0</span>
</div>

## What is compaction?
In the context of LLM agents, compaction is the process of managing a session's "memory" (context window). As a conversation grows, it consumes more tokens. Compaction automatically trims or compresses older parts of the history so the agent stays within its limits while still remembering the most important recent details. Think of it as "auto-archiving" a long email thread so you only see the most relevant replies

## Types of compaction
- Context
- Token

## When to use each
| Feature | Sliding Window | Token-based |
| :--- | :--- | :--- |
| **Trigger** | Number of events (turns) | Estimated token count |
| **Best For** | Consistent, short chat interactions | Large payloads, variable input sizes |
| **Key Parameters** | `compaction_interval`, `overlap_size` | `token_threshold`, `event_retention_size` |
| **Precedence** | Secondary | Primary (if triggered) |

> [!NOTE]
> If both token-based and sliding window compaction are active, token-based compaction takes priority. If the token threshold triggers a compaction, the sliding window check is skipped for that turn.

## Configure context compaction

Add context compaction to your agent workflow by adding an Events Compaction
Configuration setting to the App object (Python/Java) or by configuring `contextCompactors`
on the `LlmAgent` (TypeScript). As part of the
configuration, you must specify a compaction interval and overlap size (Python/Java)
or a token threshold and event retention size (TypeScript), as shown
in the following sample code:

=== "Python"

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

=== "Java"

    ```java
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
    ```

=== "TypeScript"

    ```typescript
    import {Gemini, LlmAgent, LlmSummarizer, TokenBasedContextCompactor} from '@google/adk';

    const agent = new LlmAgent({
      name: 'my-agent',
      model: 'gemini-flash-latest',
      contextCompactors: [
        new TokenBasedContextCompactor({
          tokenThreshold: 1000, // Trigger compaction when session exceeds 1000 tokens.
          eventRetentionSize: 1, // Keep at least 1 raw event (overlap).
          summarizer: new LlmSummarizer({
            llm: new Gemini({model: 'gemini-flash-latest'}),
          }),
        }),
      ],
    });
    ```

Once configured, the ADK `Runner` handles the compaction process in the
background each time the session reaches the interval.

## Example of context compaction

If you set `compaction_interval` to 3 and `overlap_size` to 1, the event data is
compressed upon completion of events 3, 6, 9, and so on. The overlap setting
increases size of the second summary compression, and each summary afterwards,
as shown in Figure 1.

![Context compaction example illustration](/assets/context-compaction.svg)
**Figure 1.** Illustration of event compaction configuration with an interval of 3
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
*   **`summarizer`**: (Optional) Define a summarizer object including a specific AI model
    to use for summarization. For more information, see
    [Define a Summarizer](#define-summarizer).

### Define a Summarizer {#define-summarizer}
You can customize the process of context compression by defining a summarizer.
The `LlmEventSummarizer` (Python/Java) or `LlmSummarizer` (TypeScript) class allows
you to specify a particular model for summarization.
The following code example demonstrates how to define and configure a custom summarizer:

=== "Python"

    ```python
    from google.adk.apps.app import App, EventsCompactionConfig
    from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
    from google.adk.models import Gemini

    # Define the AI model to be used for summarization:
    summarization_llm = Gemini(model="gemini-flash-latest")

    # Create the summarizer with the custom model:
    my_summarizer = LlmEventSummarizer(llm=summarization_llm)

    # Configure the App with the custom summarizer and compaction settings:
    app = App(
        name='my-agent',
        root_agent=root_agent,
        events_compaction_config=EventsCompactionConfig(
            compaction_interval=3,
            overlap_size=1,
            summarizer=my_summarizer,
        ),
    )
    ```

=== "Java"

    ```java
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
    ```

=== "TypeScript"

    ```typescript
    import {Gemini, LlmAgent, LlmSummarizer, TokenBasedContextCompactor} from '@google/adk';

    // Define the AI model to be used for summarization:
    const summarizationLlm = new Gemini({model: 'gemini-flash-latest'});

    // Create the summarizer with the custom model:
    const mySummarizer = new LlmSummarizer({llm: summarizationLlm});

    // Configure the agent with the custom summarizer and compaction settings:
    const agent = new LlmAgent({
      name: 'my-agent',
      model: 'gemini-flash-latest',
      contextCompactors: [
        new TokenBasedContextCompactor({
          tokenThreshold: 1000,
          eventRetentionSize: 1,
          summarizer: mySummarizer,
        }),
      ],
    });
    ```

You can further refine the compactor by modifying its summarizer. In Python and Java,
customize the `prompt_template` on `LlmEventSummarizer`. In TypeScript, customize
the `prompt` on `LlmSummarizer`. For more details, see the
[`LlmEventSummarizer` code](https://github.com/google/adk-python/blob/main/src/google/adk/apps/llm_event_summarizer.py#L60) or
[`LlmSummarizer` code](https://github.com/google/adk-js/blob/main/core/src/context/summarizers/llm_summarizer.ts).

## Token-based compaction

### What is it?
Token-based compaction triggers context management based on the volume of data (tokens) rather than the number of turns (events). This is more precise for applications with highly variable input sizes, such as code reviews or document analysis.

### Applications
- **Cost Management**: Prevents unexpected spikes in API costs by capping token usage per turn.
- **Performance Stability**: Keeps the context size optimal for model reasoning, avoiding the "lost in the middle" phenomenon.
- **Long-running Sessions**: Ideal for agents that stay active for hours or days where event counts don't accurately reflect memory usage.
  
### How it relates to context compaction?
While standard compaction looks at how many things happened, token-based compaction looks at how big those things were. If both are configured, Token-based Compaction takes precedence. If the token threshold is crossed, the system will compact the history even if the event interval hasn't been reached yet.

## Configuration settings

The configuration settings for this feature control how frequently event data is compressed of the prior event data.
*   **`overlap_size`**: Set how many of the previously compacted events are included in a
    newly compacted context set.
*   **`token_threshold`**: The token count that triggers compaction.
*   **`event_retention_size`**: The number of recent raw events to keep uncompressed.
*   **`summarizer`**: (Optional) Define a summarizer object including a specific AI model
    to use for summarization. For more information, see
    [Define a Summarizer](#define-summarizer).
