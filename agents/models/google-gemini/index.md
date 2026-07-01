# Google Gemini models for ADK agents

Supported in ADKPython v0.1.0Typescript v0.2.0Go v0.1.0Java v0.2.0Kotlin v0.1.0

ADK supports the Google Gemini family of generative AI models that provide a powerful set of models with a wide range of features. ADK provides support for many Gemini features, including [Code Execution](/integrations/code-execution/), [Google Search](/integrations/google-search/), [Context caching](/context/caching/), [Computer use](/integrations/computer-use/) and the [Interactions API](#interactions-api).

## Get started

The following code examples show a basic implementation for using Gemini models in your agents:

```python
from google.adk.agents import LlmAgent

# --- Example using a stable Gemini Flash model ---
agent_gemini_flash = LlmAgent(
    # Use the latest stable Flash model identifier
    model="gemini-flash-latest",
    name="gemini_flash_agent",
    instruction="You are a fast and helpful Gemini assistant.",
    # ... other agent parameters
)
```

```typescript
import {LlmAgent} from '@google/adk';

// --- Example #2: using a powerful Gemini Pro model with API Key in model ---
export const rootAgent = new LlmAgent({
  name: 'hello_time_agent',
  model: 'gemini-flash-latest',
  description: 'Gemini flash agent',
  instruction: `You are a fast and helpful Gemini assistant.`,
});
```

```go
import (
    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/model/gemini"
    "google.golang.org/genai"
)

// --- Example using a stable Gemini Flash model ---
modelFlash, err := gemini.NewModel(ctx, "gemini-2.0-flash", &genai.ClientConfig{})
if err != nil {
    log.Fatalf("failed to create model: %v", err)
}
agentGeminiFlash, err := llmagent.New(llmagent.Config{
    // Use the latest stable Flash model identifier
    Model:       modelFlash,
    Name:        "gemini_flash_agent",
    Instruction: "You are a fast and helpful Gemini assistant.",
    // ... other agent parameters
})
if err != nil {
    log.Fatalf("failed to create agent: %v", err)
}
```

```java
// --- Example #1: using a stable Gemini Flash model with ENV variables---
LlmAgent agentGeminiFlash =
    LlmAgent.builder()
        // Use the latest stable Flash model identifier
        .model("gemini-flash-latest") // Set ENV variables to use this model
        .name("gemini_flash_agent")
        .instruction("You are a fast and helpful Gemini assistant.")
        // ... other agent parameters
        .build();
```

```kotlin
import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.models.Gemini

// --- Example using a stable Gemini Flash model ---
val agentGeminiFlash = LlmAgent(
    // Use the latest stable Flash model identifier
    name = "gemini_flash_agent",
    model = Gemini(name = "gemini-flash-latest"),
    instruction = Instruction("You are a fast and helpful Gemini assistant."),
    // ... other agent parameters
)
```

Note: Gemini model selector `gemini-flash-latest`

Most code examples in ADK documentation use `gemini-flash-latest` to select the [latest available](https://ai.google.dev/gemini-api/docs/models#latest) Gemini Flash version. However, if you access Gemini from a regional endpoint, such as `us-central1`, this selection string may not work. In that case, use a specific model version string from the [Gemini models](https://ai.google.dev/gemini-api/docs/models) page or Google Cloud [Gemini models](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models) list.

## Gemini model authentication

When using an AI model through a service, such as the Gemini API or Gemini Enterprise Agent Platform on Google Cloud, you must provide an API key or authenticate with the service. The most direct way to provide this information is to use environment variables or an `.env` file. The following examples show the most common way to configure an agent for use with the Gemini API or Gemini Enterprise Agent Platform.

```text
# .env configuration file
GOOGLE_API_KEY="PASTE_YOUR_GEMINI_API_KEY_HERE"
```

```text
# .env configuration file
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=location-code        # example: us-central1
GOOGLE_GENAI_USE_ENTERPRISE=True
```

For more details on connecting ADK agents to Google Cloud hosted models and services, including Gemini Enterprise Agent Platform, see the [Connect to Google Cloud and Agent Platform](/get-started/google-cloud/) guide.

## Voice and video streaming support

In order to use voice/video streaming in ADK, you will need to use Gemini models that support the Live API. You can find the **model ID(s)** that support the Gemini Live API in the documentation:

- [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
- [Agent Platform: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

## Gemini Interactions API

Supported in ADKPython v1.21.0

The Gemini [Interactions API](https://ai.google.dev/gemini-api/docs/interactions) is an alternative to the ***generateContent*** inference API, which provides stateful conversation capabilities, allowing you to chain interactions using a `previous_interaction_id` instead of sending the full conversation history with each request. Using this feature can be more efficient for long conversations.

You can enable the Interactions API by setting the `use_interactions_api=True` parameter in the Gemini model configuration, as shown in the following code snippet:

```python
from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools.google_search_tool import GoogleSearchTool

root_agent = Agent(
    model=Gemini(
        model="gemini-flash-latest",
        use_interactions_api=True,  # Enable Interactions API
    ),
    name="interactions_test_agent",
    tools=[
        GoogleSearchTool(bypass_multi_tools_limit=True),  # Converted to function tool
        get_current_weather,  # Custom function tool
    ],
)
```

For a complete code sample, see the [Interactions API sample](https://github.com/google/adk-python/tree/main/contributing/samples/models/interactions_api).

### Known limitations

The Interactions API **does not** support mixing custom function calling tools with built-in tools, such as the [Google Search](/integrations/google-search/), tool, within the same agent. You can work around this limitation by configuring the built-in tool to operate as a custom tool using the `bypass_multi_tools_limit` parameter:

```python
# Use bypass_multi_tools_limit=True to convert google_search to a function tool
GoogleSearchTool(bypass_multi_tools_limit=True)
```

In this example, this option converts the built-in `google_search` to a function calling tool (via `GoogleSearchAgentTool`), which allows it to work alongside custom function tools.

## Troubleshooting

### Error Code 429 - RESOURCE_EXHAUSTED

This error usually happens if the number of your requests exceeds the capacity allocated to process requests.

To mitigate this, you can do one of the following:

1. Request higher quota limits for the model you are trying to use.

1. Enable client-side retries. Retries allow the client to automatically retry the request after a delay, which can help if the quota issue is temporary.

   There are two ways you can set retry options:

   **Option 1:** Set retry options on the Agent as a part of `generate_content_config`.

   You would use this option if you are instantiating this model adapter by yourself.

   ```python
   root_agent = Agent(
       model='gemini-flash-latest',
       # ...
       generate_content_config=types.GenerateContentConfig(
           # ...
           http_options=types.HttpOptions(
               # ...
               retry_options=types.HttpRetryOptions(initial_delay=1, attempts=2),
               # ...
           ),
           # ...
       )
   ```

   ```java
   import com.google.adk.agents.LlmAgent;
   import com.google.genai.types.GenerateContentConfig;
   import com.google.genai.types.HttpOptions;
   import com.google.genai.types.HttpRetryOptions;

   // ...

   LlmAgent rootAgent = LlmAgent.builder()
       .model("gemini-flash-latest")
       // ...
       .generateContentConfig(GenerateContentConfig.builder()
           // ...
           .httpOptions(HttpOptions.builder()
               // ...
               .retryOptions(HttpRetryOptions.builder().initialDelay(1.0).attempts(2).build())
               // ...
               .build())
           // ...
           .build())
       .build();
   ```

   **Option 2:** Retry options on this model adapter.

   You would use this option if you were instantiating the instance of adapter by yourself.

   ```python
   from google.genai import types

   # ...

   agent = Agent(
       model=Gemini(
       retry_options=types.HttpRetryOptions(initial_delay=1, attempts=2),
       )
   )
   ```

   ```java
   import com.google.adk.agents.LlmAgent;
   import com.google.adk.models.Gemini;
   import com.google.genai.Client;
   import com.google.genai.types.HttpOptions;
   import com.google.genai.types.HttpRetryOptions;

   // ...

   LlmAgent agent = LlmAgent.builder()
       .model(Gemini.builder()
           .modelName("gemini-flash-latest")
           .apiClient(Client.builder()
               .httpOptions(HttpOptions.builder()
                   .retryOptions(HttpRetryOptions.builder().initialDelay(1.0).attempts(2).build())
                   .build())
               .build())
           .build())
       .build();
   ```

   In Kotlin, you can achieve this by creating the `Client` instance yourself and passing it to the `Gemini` constructor.

   ```kotlin
   import com.google.adk.kt.agents.LlmAgent
   import com.google.adk.kt.models.Gemini
   import com.google.genai.Client
   import com.google.genai.types.HttpOptions
   import com.google.genai.types.HttpRetryOptions

   val client = Client.builder()
       .apiKey("YOUR_API_KEY")
       .httpOptions(HttpOptions.builder()
           .retryOptions(HttpRetryOptions.builder().initialDelay(1.0).attempts(2).build())
           .build())
       .build()

   val model = Gemini(client = client, name = "gemini-flash-latest")

   val agent = LlmAgent(
       name = "my_agent",
       model = model
       // ...
   )
   ```
