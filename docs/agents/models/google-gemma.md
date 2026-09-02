# Google Gemma models for ADK agents

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span>
</div>

ADK agents can use the [Google Gemma](https://ai.google.dev/gemma/docs) family of generative AI models that offer a
wide range of capabilities. ADK supports many Gemma features,
including [Tool Calling](/tools-custom/)
and [Structured Output](/agents/llm-agents/#structuring-data-input_schema-output_schema-output_key).

You can use Gemma 4 through the [Gemini API](https://ai.google.dev/gemini-api/docs),
or with one of many self-hosting options on Google Cloud:
[Agent Platform](https://console.cloud.google.com/vertex-ai/publishers/google/model-garden/gemma4),
[Google Kubernetes Engine](https://docs.cloud.google.com/kubernetes-engine/docs/tutorials/serve-gemma-gpu-vllm),
[Cloud Run](https://docs.cloud.google.com/run/docs/run-gemma-on-cloud-run).

Gemma 3 needs a different model class than the Gemma 4 examples below. It has
no native function calling or system instruction support, so ADK supplies
workarounds in dedicated classes: use `Gemma(model="gemma-3-27b-it")` for the
Gemini API and `Gemma3Ollama()` for Ollama, both from `google.adk.models`.
`Gemma3Ollama` is only defined when [LiteLLM](/agents/models/litellm/) is
installed (`litellm>=1.84`).

## Gemini API Example

Create an API key in [Google AI Studio](https://aistudio.google.com/app/apikey).

=== "Python"
    ```python
    --8<-- "examples/inline/python/agents/models/google-gemma/001-gemini-api-example.py"
    ```

=== "Java"
    ```java
    --8<-- "examples/inline/java/agents/models/google-gemma/002-gemini-api-example.java"
    ```

## vLLM Example

To access Gemma 4 endpoints in these services,
you can use vLLM models through the [LiteLLM](/agents/models/litellm/) library for Python, 
and through [LangChain4j](https://docs.langchain4j.dev/) for Java.

The following example shows how to use a Gemma 4 vLLM endpoint with ADK agents.

### Setup

1. **Deploy Model:** Deploy your chosen model using
    [Agent Platform](https://console.cloud.google.com/vertex-ai/publishers/google/model-garden/gemma4),
    [Google Kubernetes Engine](https://docs.cloud.google.com/kubernetes-engine/docs/tutorials/serve-gemma-gpu-vllm),
    or [Cloud Run](https://docs.cloud.google.com/run/docs/run-gemma-on-cloud-run),
    and use its OpenAI-compatible API endpoint.
    Note that the API base URL includes `/v1` (e.g., `https://your-vllm-endpoint.run.app/v1`).
    * *Important for ADK Tools:* When deploying, ensure the serving tool
        supports and enables compatible tool/function calling and reasoning parsers.
2. **Authentication:** Determine how your endpoint handles authentication (e.g.,
   API key, bearer token).

### Code

=== "Python"
    ```python
    --8<-- "examples/inline/python/agents/models/google-gemma/003-code.py"
    ```

=== "Java"
    To use Gemma hosted on vLLM, you must use an OpenAI compatible library.
    LangChain4j offers an OpenAI dependency that you can add to your `pom.xml`:
    ```xml
    <!-- LangChain4j to ADK bridge -->
    <dependency>
        <groupId>com.google.adk</groupId>
        <artifactId>google-adk-langchain4j</artifactId>
        <version>${adk.version}</version>
    </dependency>
    <!-- Core LangChain4j library -->
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-core</artifactId>
        <version>${langchain4j.version}</version>
    </dependency>
    <!-- OpenAI compatible model -->
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-open-ai</artifactId>
        <version>${langchain4j.version}</version>
    </dependency>
    ```

    Create an OpenAI compatible chat model (streaming or non-streaming),
    wrap it with the `LangChain4j` wrapper,
    then pass it to the `LlmAgent`:
    ```java
    --8<-- "examples/inline/java/agents/models/google-gemma/004-code.java"
    ```

## Build a food tour agent with Gemma 4, ADK, and Google Maps MCP
This sample shows how to build a personalized food tour agent using Gemma 4, ADK, and the Google Maps MCP server. The agent takes a user’s dish photo or text description, a location, and an optional budget, then recommends places to eat and organizes them into a walking route.

### Prerequisites

- Get an API key in [Google AI Studio](https://aistudio.google.com/app/apikey).
  Set `GEMINI_API_KEY` environment variable to your Gemini API key.
- Enable [Google Maps API](https://console.cloud.google.com/maps-api/) on Google Cloud Console.
- Create a [Google Maps Platform API key](https://console.cloud.google.com/maps-api/credentials).
  Set `MAPS_API_KEY` environment variable to your API key.
- Install ADK and configure it in your Python environment 
  or configure the Java dependencies in your Java project.

### Project structure
```bash
food_tour_app/
├── __init__.py
└── agent.py
```

`agent.py`
```python
--8<-- "examples/inline/python/agents/models/google-gemma/005-project-structure.py"
```

### Environment variables
Set the required environment variables before running the agent.
```
export MAPS_API_KEY="YOUR_GOOGLE_MAPS_API_KEY"
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

### Example usage
To test out the capabilities of the Food Tour Agent, try pasting one of these prompts into the chat:

- *"I want to do a ramen tour in Toronto. My budget is $60 for the day. Give me a walking route for the top 3 spots and tell me what I should order at each."*
- *"I have this photo of a deep dish pizza [insert image URL]. I want to find the best places for this around Navy Pier in Chicago. Structure a walking tour and tell me what the must-have slice is at each stop."*
- *"I'm in Downtown Austin looking for an authentic BBQ tour. Let's keep the budget under $100. Build a walking route between 3 highly-rated spots and give me insider tips on the best cuts of meat to get."*

The agent will:

1. Infer the likely cuisine or dish style
2. Search for relevant places using Google Maps MCP tools
3. Compute a walking route between selected stops
4. Return a structured food tour with recommendations and insider tips
