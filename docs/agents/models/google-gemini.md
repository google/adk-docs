# Google Gemini models for ADK agents

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.2.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

ADK supports the Google Gemini family of generative AI models that provide a
powerful set of models with a wide range of features. ADK provides support for many
Gemini features, including
[Code Execution](/integrations/code-execution/),
[Google Search](/integrations/google-search/),
[Context caching](/context/caching/),
[Computer use](/integrations/computer-use/)
and the [Interactions API](#interactions-api).

## Get started

The following code examples show a basic implementation for using Gemini models
in your agents:

=== "Python"

    ```python
    --8<-- "examples/inline/python/agents/models/google-gemini/001-get-started.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/agents/models/google-gemini/002-get-started.ts"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/agents/models/google-gemini/003-get-started.go.txt"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/agents/models/google-gemini/004-get-started.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/inline/kotlin/agents/models/google-gemini/005-get-started.kt"
    ```

??? note "Note: Gemini model selector `gemini-flash-latest`"

    Most code examples in ADK documentation use `gemini-flash-latest` to select the
    [latest available](https://ai.google.dev/gemini-api/docs/models#latest)
    Gemini Flash version. However, if you access Gemini from a regional endpoint,
    such as `us-central1`, this selection string may not work. In that case,
    use a specific model version string from the
    [Gemini models](https://ai.google.dev/gemini-api/docs/models) page or
    Google Cloud [Gemini models](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models) list.

## Gemini model authentication

When using an AI model through a service, such as the Gemini API or Gemini
Enterprise Agent Platform on Google Cloud, you must provide an API key or
authenticate with the service. The most direct way to provide this information
is to use environment variables or an `.env` file. The following examples show
the most common way to configure an agent for use with the Gemini API or Gemini
Enterprise Agent Platform.

=== "Gemini API"

    ```
    # .env configuration file
    GOOGLE_API_KEY="PASTE_YOUR_GEMINI_API_KEY_HERE"
    ```

=== "Google Cloud Agent Platform"

    ```
    # .env configuration file
    GOOGLE_CLOUD_PROJECT=your-project-id
    GOOGLE_CLOUD_LOCATION=location-code        # example: us-central1
    GOOGLE_GENAI_USE_ENTERPRISE=True
    ```

For more details on connecting ADK agents to Google Cloud hosted models and services,
including Gemini Enterprise Agent Platform, see the
[Connect to Google Cloud and Agent Platform](/get-started/google-cloud/) guide.

## Voice and video streaming support

In order to use voice/video streaming in ADK, you will need to use Gemini
models that support the Live API. You can find the **model ID(s)** that
support the Gemini Live API in the documentation:

- [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
- [Agent Platform: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

## Gemini Interactions API {#interactions-api}

<div class="language-support-tag">
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

=== "Python"

    ```python
    --8<-- "examples/inline/python/agents/models/google-gemini/006-gemini-interactions-api-interactions-api.py"
    ```

For a complete code sample, see the
[Interactions API sample](https://github.com/google/adk-python/tree/main/contributing/samples/models/interactions_api).

### Known limitations

The Interactions API **does not** support mixing custom function calling tools with
built-in tools, such as the
[Google Search](/integrations/google-search/),
tool, within the same agent. You can work around this limitation by configuring the
built-in tool to operate as a custom tool using the `bypass_multi_tools_limit`
parameter:

=== "Python"

    ```python
    --8<-- "examples/inline/python/agents/models/google-gemini/007-known-limitations.py"
    ```

In this example, this option converts the built-in `google_search` to a function
calling tool (via `GoogleSearchAgentTool`), which allows it to work alongside
custom function tools.

## Troubleshooting

### Error Code 429 - RESOURCE_EXHAUSTED

This error usually happens if the number of your requests exceeds the capacity allocated to process requests.

To mitigate this, you can do one of the following:

1.  Request higher quota limits for the model you are trying to use.

2.  Enable client-side retries. Retries allow the client to automatically retry the request after a delay, which can help if the quota issue is temporary.

    There are two ways you can set retry options:

    **Option 1:** Set retry options on the Agent as a part of `generate_content_config`.

    You would use this option if you are passing the model as a name string and
    letting ADK create the model adapter for you.

    === "Python"

        ```python
        --8<-- "examples/inline/python/agents/models/google-gemini/008-error-code-429-resourceexhausted.py"
        ```

    === "Java"

        ```java
        --8<-- "examples/inline/java/agents/models/google-gemini/009-error-code-429-resourceexhausted.java"
        ```

    **Option 2:** Retry options on this model adapter.

    You would use this option if you were instantiating the instance of adapter
    by yourself.

    === "Python"

        ```python
        --8<-- "examples/inline/python/agents/models/google-gemini/010-error-code-429-resourceexhausted.py"
        ```

    === "Java"

        ```java
        --8<-- "examples/inline/java/agents/models/google-gemini/011-error-code-429-resourceexhausted.java"
        ```

    === "Kotlin"

        In Kotlin, you can achieve this by creating the `Client` instance yourself and passing it to the `Gemini` constructor.

        ```kotlin
        --8<-- "examples/inline/kotlin/agents/models/google-gemini/012-error-code-429-resourceexhausted.kt"
        ```
