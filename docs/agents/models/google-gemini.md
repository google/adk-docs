# Google Gemini models for ADK agents

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">Typescript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

ADK supports the Google Gemini family of generative AI models that provide a
powerful set of models with a wide range of features. ADK provides support for many
Gemini features, including
[Code Execution](/adk-docs/tools/gemini-api/code-execution/),
[Google Search](/adk-docs/tools/gemini-api/google-search/),
[Context caching](/adk-docs/context/caching/),
[Computer use](/adk-docs/tools/gemini-api/computer-use/)
and the [Interactions API](#interactions-api).

## Get started

The following code examples show a basic implementation for using Gemini models
in your agents:

=== "Python"

    ```python
    from google.adk.agents import LlmAgent

    # --- Example using a stable Gemini Flash model ---
    agent_gemini_flash = LlmAgent(
        # Use the latest stable Flash model identifier
        model="gemini-2.5-flash",
        name="gemini_flash_agent",
        instruction="You are a fast and helpful Gemini assistant.",
        # ... other agent parameters
    )
    ```

=== "TypeScript"

    ```typescript
    import {LlmAgent} from '@google/adk';

    // --- Example #2: using a powerful Gemini Pro model with API Key in model ---
    export const rootAgent = new LlmAgent({
      name: 'hello_time_agent',
      model: 'gemini-2.5-flash',
      description: 'Gemini flash agent',
      instruction: `You are a fast and helpful Gemini assistant.`,
    });
    ```

=== "Go"

    ```go
    import (
    	"google.golang.org/adk/agent/llmagent"
    	"google.golang.org/adk/model/gemini"
    	"google.golang.org/genai"
    )

    --8<-- "examples/go/snippets/agents/models/models.go:gemini-example"
    ```

=== "Java"

    ```java
    // --- Example #1: using a stable Gemini Flash model with ENV variables---
    LlmAgent agentGeminiFlash =
        LlmAgent.builder()
            // Use the latest stable Flash model identifier
            .model("gemini-2.5-flash") // Set ENV variables to use this model
            .name("gemini_flash_agent")
            .instruction("You are a fast and helpful Gemini assistant.")
            // ... other agent parameters
            .build();
    ```


## Gemini model authentication

This section covers authenticating with Google's Gemini models, either through Google AI Studio for rapid development or Google Cloud Vertex AI for enterprise applications. This is the most direct way to use Google's flagship models within ADK.

**Integration Method:** Once you are authenticated using one of the below methods, you can pass the model's identifier string directly to the
`model` parameter of `LlmAgent`.


!!! tip

    The `google-genai` library, used internally by ADK for Gemini models, can connect
    through either Google AI Studio or Vertex AI.

    **Model support for voice/video streaming**

    In order to use voice/video streaming in ADK, you will need to use Gemini
    models that support the Live API. You can find the **model ID(s)** that
    support the Gemini Live API in the documentation:

    - [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
    - [Vertex AI: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

### Google AI Studio

This is the simplest method and is recommended for getting started quickly.

*   **Authentication Method:** API Key
*   **Setup:**
    1.  **Get an API key:** Obtain your key from [Google AI Studio](https://aistudio.google.com/apikey).
    2.  **Set environment variables:** Create a `.env` file (Python) or `.properties` (Java) in your project's root directory and add the following lines. ADK will automatically load this file.

        ```shell
        export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
        export GOOGLE_GENAI_USE_VERTEXAI=FALSE
        ```

        (or)

        Pass these variables during the model initialization via the `Client` (see example below).

* **Models:** Find all available models on the
  [Google AI for Developers site](https://ai.google.dev/gemini-api/docs/models).

### Google Cloud Vertex AI

For scalable and production-oriented use cases, Vertex AI is the recommended platform. Gemini on Vertex AI supports enterprise-grade features, security, and compliance controls. Based on your development environment and usecase, *choose one of the below methods to authenticate*.

**Pre-requisites:** A Google Cloud Project with [Vertex AI enabled](https://console.cloud.google.com/apis/enableflow;apiid=aiplatform.googleapis.com).

### **Method A: User Credentials (for Local Development)**

1.  **Install the gcloud CLI:** Follow the official [installation instructions](https://cloud.google.com/sdk/docs/install).
2.  **Log in using ADC:** This command opens a browser to authenticate your user account for local development.
    ```bash
    gcloud auth application-default login
    ```
3.  **Set environment variables:**
    ```shell
    export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    export GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION" # e.g., us-central1
    ```

    Explicitly tell the library to use Vertex AI:

    ```shell
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

4. **Models:** Find available model IDs in the
  [Vertex AI documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models).

### **Method B: Vertex AI Express Mode**
[Vertex AI Express Mode](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview) offers a simplified, API-key-based setup for rapid prototyping.

1.  **Sign up for Express Mode** to get your API key.
2.  **Set environment variables:**
    ```shell
    export GOOGLE_API_KEY="PASTE_YOUR_EXPRESS_MODE_API_KEY_HERE"
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

### **Method C: Service Account (for Production & Automation)**

For deployed applications, a service account is the standard method.

1.  [**Create a Service Account**](https://cloud.google.com/iam/docs/service-accounts-create#console) and grant it the `Vertex AI User` role.
2.  **Provide credentials to your application:**
    *   **On Google Cloud:** If you are running the agent in Cloud Run, GKE, VM or other Google Cloud services, the environment can automatically provide the service account credentials. You don't have to create a key file.
    *   **Elsewhere:** Create a [service account key file](https://cloud.google.com/iam/docs/keys-create-delete#console) and point to it with an environment variable:
        ```bash
        export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/keyfile.json"
        ```
    Instead of the key file, you can also authenticate the service account using Workload Identity. But this is outside the scope of this guide.

!!! warning "Secure Your Credentials"

    Service account credentials or API keys are powerful credentials. Never
    expose them publicly. Use a secret manager such as [Google Cloud Secret
    Manager](https://cloud.google.com/security/products/secret-manager) to store
    and access them securely in production.

!!! note "Gemini model versions"

    Always check the official Gemini documentation for the latest model names,
    including specific preview versions if needed. Preview models might have
    different availability or quota limitations.

## Troubleshooting

### Error Code 429 - RESOURCE_EXHAUSTED

This error usually happens if the number of your requests exceeds the capacity allocated to process requests.

To mitigate this, you can do one of the following:

1.  Request higher quota limits for the model you are trying to use.

2.  Enable client-side retries. Retries allow the client to automatically retry the request after a delay, which can help if the quota issue is temporary.

    There are two ways you can set retry options:

    **Option 1:** Set retry options on the Agent as a part of generate_content_config.

    You would use this option if you are instantiating this model adapter by
    yourself.

    ```python
    root_agent = Agent(
        model='gemini-2.5-flash',
        ...
        generate_content_config=types.GenerateContentConfig(
            ...
            http_options=types.HttpOptions(
                ...
                retry_options=types.HttpRetryOptions(initial_delay=1, attempts=2),
                ...
            ),
            ...
        )
    ```

    **Option 2:** Retry options on this model adapter.

    You would use this option if you were instantiating the instance of adapter
    by yourself.

    ```python
    from google.genai import types

    # ...

    agent = Agent(
        model=Gemini(
        retry_options=types.HttpRetryOptions(initial_delay=1, attempts=2),
        )
    )
    ```

## Gemini Interactions API {#interactions-api}

<div class="language-support-tag" title="Java ADK currently supports Gemini and Anthropic models.">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.21.0</span>
</div>

The Gemini [Interactions API](https://ai.google.dev/gemini-api/docs/interactions)
is an alternative to the ***generateContent*** inference API, which provides
stateful conversation capabilities, allowing you to chain interactions using a
`previous_interaction_id` instead of sending the full conversation history with
each request. Using this feature can be more efficient for long conversations.

You can enable the Interactions API by setting the `use_interactions_api=True`
parameter in the Gemini model configuration, as shown in the following code
snippet:

```python
from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools.google_search_tool import GoogleSearchTool

root_agent = Agent(
    model=Gemini(
        model="gemini-2.5-flash",
        use_interactions_api=True,  # Enable Interactions API
    ),
    name="interactions_test_agent",
    tools=[
        GoogleSearchTool(bypass_multi_tools_limit=True),  # Converted to function tool
        get_current_weather,  # Custom function tool
    ],
)
```

For a complete code sample, see the
[Interactions API sample](https://github.com/google/adk-python/tree/main/contributing/samples/interactions_api).

### Known limitations

The Interactions API **does not** support mixing custom function calling tools with
built-in tools, such as the
[Google Search](/adk-docs/tools/built-in-tools/#google-search),
tool, within the same agent. You can work around this limitation by configuring the
the built-in tool to operate as a custom tool using the `bypass_multi_tools_limit`
parameter:

```python
# Use bypass_multi_tools_limit=True to convert google_search to a function tool
GoogleSearchTool(bypass_multi_tools_limit=True)
```

In this example, this option converts the built-in google_search to a function
calling tool (via GoogleSearchAgentTool), which allows it to work alongside
custom function tools.
