# Agent Platform hosted models for ADK agents

For enterprise-grade scalability, reliability, and integration with Google
Cloud's MLOps ecosystem, you can use models deployed to Agent Platform Endpoints.
This includes models from Model Garden or your own fine-tuned models.

**Integration Method:** Pass the full Agent Platform Endpoint resource string
(`projects/PROJECT_ID/locations/LOCATION/endpoints/ENDPOINT_ID`) directly to the
`model` parameter of `LlmAgent`.

## Agent Platform Setup

For more details on connecting ADK agents to Google Cloud hosted models and services,
including Gemini Enterprise Agent Platform, see the
[Connect to Google Cloud and Agent Platform](/get-started/google-cloud/) guide.

## Model Garden Deployments

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.2.0</span><span class="lst-java">Java v0.1.0</span>
</div>

You can deploy various open and proprietary models from the
[Model Garden](https://console.cloud.google.com/vertex-ai/model-garden)
to an endpoint.

**Example:**

=== "Python"

    ```python
    --8<-- "examples/inline/python/agents/models/agent-platform/001-model-garden-deployments.py"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/agents/models/agent-platform/002-model-garden-deployments.java"
    ```

## Fine-tuned Model Endpoints

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.2.0</span><span class="lst-java">Java v0.1.0</span>
</div>

Deploying your fine-tuned models (whether based on Gemini or other architectures
supported by Agent Platform) results in an endpoint that can be used directly.

**Example:**

=== "Python"

    ```python
    --8<-- "examples/inline/python/agents/models/agent-platform/003-fine-tuned-model-endpoints.py"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/agents/models/agent-platform/004-fine-tuned-model-endpoints.java"
    ```

## Anthropic Claude on Agent Platform {#anthropic-claude}

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.2.0</span><span class="lst-java">Java v0.1.0</span>
</div>

Some providers, like Anthropic, make their models available directly through
Agent Platform.

**Example:**

=== "Python"

    **Integration Method:** Uses the direct model string (e.g.,
    `"claude-3-sonnet@20240229"`).

    **How Resolution Works:** ADK's registry automatically recognizes `gemini-*`
    strings and standard Agent Platform endpoint strings
    (`projects/.../locations/.../endpoints/...`) and routes them via the `google-genai`
    library. Claude model strings matching `claude-3-*` or `claude-*-4*` route
    to the `Claude` wrapper class the same way. For a Claude model identifier
    that does not match those patterns, import `Claude` from
    `google.adk.models` and pass an instance instead of a string:
    `LlmAgent(model=Claude(model="..."), ...)`.

    **Setup:**

    1. **Agent Platform Environment:** Ensure the consolidated Agent Platform setup (ADC, Env
       Vars, `GOOGLE_GENAI_USE_ENTERPRISE=TRUE`) is complete.

    2. **Install Provider Library:** Install the necessary client library configured
       for Agent Platform.

        ```shell
        pip install "anthropic[vertex]"
        ```

    3. **Create the Agent:** Pass the Claude model string to `LlmAgent`:

       ```python
       --8<-- "examples/inline/python/agents/models/agent-platform/005-anthropic-claude-on-agent-platform-anthr.py"
       ```

=== "Java"

    **Integration Method:** Directly instantiate the provider-specific model class (e.g., `com.google.adk.models.Claude`) and configure it with an Agent Platform backend.

    **Why Direct Instantiation?** The Java ADK's `LlmRegistry` primarily handles Gemini models by default. For third-party models like Claude on Agent Platform, you directly provide an instance of the ADK's wrapper class (e.g., `Claude`) to the `LlmAgent`. This wrapper class is responsible for interacting with the model via its specific client library, configured for Agent Platform.

    **Setup:**

    1.  **Agent Platform Environment:**
        *   Ensure your Google Cloud project and region are correctly set up.
        *   **Application Default Credentials (ADC):** Make sure ADC is configured correctly in your environment. This is typically done by running `gcloud auth application-default login`. The Java client libraries use these credentials to authenticate with Agent Platform. Follow the [Google Cloud Java documentation on ADC](https://cloud.google.com/java/docs/reference/google-auth-library/latest/com.google.auth.oauth2.GoogleCredentials#com_google_auth_oauth2_GoogleCredentials_getApplicationDefault__) for detailed setup.

    2.  **Provider Library Dependencies:**
        *   **Third-Party Client Libraries (Often Transitive):** The ADK core library often includes the necessary client libraries for common third-party models on Agent Platform (like Anthropic's required classes) as **transitive dependencies**. This means you might not need to explicitly add a separate dependency for the Anthropic Vertex SDK in your `pom.xml` or `build.gradle`.

    3.  **Instantiate and Configure the Model:**
        When creating your `LlmAgent`, instantiate the `Claude` class (or the equivalent for another provider) and configure its `VertexBackend`.

    ```java
    --8<-- "examples/inline/java/agents/models/agent-platform/006-anthropic-claude-on-agent-platform-anthr.java"
    ```

### Adaptive thinking

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.34.0</span>
</div>

Newer Claude models support *adaptive* extended thinking, where the model chooses
its reasoning depth itself rather than using a fixed token budget. On the native
Claude path, a negative `thinking_budget` maps to adaptive thinking.

The recommended way to control reasoning depth is the `effort` field on
`AnthropicGenerateContentConfig`:

```python
--8<-- "examples/inline/python/agents/models/agent-platform/007-adaptive-thinking.py"
```

*   The standard `thinking_config.thinking_level` is not supported for Claude.
    Setting it on `AnthropicGenerateContentConfig` raises a validation error; on
    a plain `types.GenerateContentConfig` it is ignored with a warning. Use
    `effort` instead.

## Open Models on Agent Platform {#open-models}

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

Agent Platform offers a curated selection of open-source models, such as Meta Llama, through Model-as-a-Service (MaaS). These models are accessible via managed APIs, allowing you to deploy and scale without managing the underlying infrastructure. For a full list of available options, see the [Agent Platform open models for MaaS](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/maas/use-open-models#open-models) documentation.

=== "Python"

    You can use the [LiteLLM](https://docs.litellm.ai/) library to access open models like Meta's Llama on Agent Platform MaaS

    **Integration Method:** Use the `LiteLlm` wrapper class and set it
    as the `model` parameter of `LlmAgent`. Make sure you go through the [LiteLLM model connector for ADK agents](/agents/models/litellm/#litellm-model-connector-for-adk-agents) documentation on how to use LiteLLM in ADK

    **Setup:**

    1. **Agent Platform Environment:** Ensure the consolidated Agent Platform setup (ADC, Env
       Vars, `GOOGLE_GENAI_USE_ENTERPRISE=TRUE`) is complete.

    2. **Install LiteLLM:** ADK requires `litellm>=1.84`.
            ```shell
            pip install "litellm>=1.84"
            ```

    **Example:**

    ```python
    --8<-- "examples/inline/python/agents/models/agent-platform/008-open-models-on-agent-platform-open-model.py"
    ```
