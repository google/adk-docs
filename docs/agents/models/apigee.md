# Apigee AI Gateway for ADK agents

<div class="language-support-tag">
   <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.18.0</span><span class="lst-java">Java v0.4.0</span>
</div>

[Apigee](https://docs.cloud.google.com/apigee/docs/api-platform/get-started/what-apigee)
provides a powerful [AI Gateway](https://cloud.google.com/solutions/apigee-ai),
transforming how you manage and govern your generative AI model traffic. By
exposing your AI model endpoint (like Vertex AI or the Gemini API) through an
Apigee proxy, you immediately gain enterprise-grade capabilities:

- **Model Safety:** Implement security policies like Model Armor for threat protection.

- **Traffic Governance:** Enforce Rate Limiting and Token Limiting to manage costs and prevent abuse.

- **Performance:** Improve response times and efficiency using Semantic Caching and advanced model routing.

- **Monitoring & Visibility:** Get granular monitoring, analysis, and auditing of all your AI requests.

!!! note

    The `ApigeeLLM` wrapper is designed for use with Vertex AI, the Gemini API (`generateContent`), and any OpenAI-compatible API (such as the `/chat/completions` endpoint).

## Example implementation

Integrate Apigee's governance into your agent's workflow by instantiating the
`ApigeeLlm` wrapper object and pass it to an `LlmAgent` or other agent type.

### Using Vertex AI and Gemini APIs

When using `ApigeeLlm` with Vertex AI or the Gemini API, the configuration is optimized for their `generateContent` endpoints.

=== "Python"

    ```python

    from google.adk.agents import LlmAgent
    from google.adk.models.apigee_llm import ApigeeLlm

    # Instantiate the ApigeeLlm wrapper
    model = ApigeeLlm(
        # Specify the Apigee route to your model. For more info, check out the ApigeeLlm documentation (https://github.com/google/adk-python/tree/main/contributing/samples/hello_world_apigeellm).
        model="apigee/gemini-2.5-flash",
        # The proxy URL of your deployed Apigee proxy including the base path
        proxy_url=f"https://{APIGEE_PROXY_URL}",
        # Pass necessary authentication/authorization headers (like an API key)
        custom_headers={"foo": "bar"}
    )

    # Pass the configured model wrapper to your LlmAgent
    agent = LlmAgent(
        model=model,
        name="my_governed_agent",
        instruction="You are a helpful assistant powered by Gemini and governed by Apigee.",
        # ... other agent parameters
    )

    ```

=== "Java"

    ```java
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.models.ApigeeLlm;
    import com.google.common.collect.ImmutableMap;

    ApigeeLlm apigeeLlm =
            ApigeeLlm.builder()
                .modelName("apigee/gemini-2.5-flash") // Specify the Apigee route to your model. For more info, check out the ApigeeLlm documentation
                .proxyUrl(APIGEE_PROXY_URL) //The proxy URL of your deployed Apigee proxy including the base path
                .customHeaders(ImmutableMap.of("foo", "bar")) //Pass necessary authentication/authorization headers (like an API key)
                .build();
    LlmAgent agent =
        LlmAgent.builder()
            .model(apigeeLlm)
            .name("my_governed_agent")
            .description("my_governed_agent")
            .instruction("You are a helpful assistant powered by Gemini and governed by Apigee.")
            // tools will be added next
            .build();
    ```

### Using OpenAI-compatible APIs

The `ApigeeLlm` wrapper can also connect to any OpenAI-compatible API that uses the `/chat/completions` endpoint. This allows you to apply Apigee's governance features to a wider range of models.

You can configure the wrapper for an OpenAI-compatible API in two ways:

1.  **Using the `model` string:** Set the model provider to `openai`.
2.  **Using the `api_type` parameter:** Explicitly set the `api_type` to `chat_completions`.

=== "Python"

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.models.apigee_llm import ApigeeLlm

    # Option 1: Configure using the model string
    model_from_string = ApigeeLlm(
        model="apigee/openai/gpt-4",
        proxy_url=f"https://{APIGEE_PROXY_URL}",
        custom_headers={"Authorization": f"Bearer {OPENAI_API_KEY}"}
    )

    # Option 2: Configure using the api_type parameter
    model_from_api_type = ApigeeLlm(
        model="apigee/gpt-4",
        api_type="chat_completions",
        proxy_url=f"https://{APIGEE_PROXY_URL}",
        custom_headers={"Authorization": f"Bearer {OPENAI_API_KEY}"}
    )

    # Pass the configured model to your agent
    agent = LlmAgent(
        model=model_from_string, # or model_from_api_type
        name="my_openai_agent",
        instruction="You are a helpful assistant powered by an OpenAI model and governed by Apigee.",
    )
    ```

With this configuration, every API call from your agent will be routed through
Apigee first, where all necessary policies (security, rate limiting, logging)
are executed before the request is securely forwarded to the underlying AI model
endpoint. For a full code example using the Apigee proxy, see
[Hello World Apigee LLM](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world_apigeellm).