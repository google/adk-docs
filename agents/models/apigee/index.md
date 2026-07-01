# Apigee AI Gateway for ADK agents

Supported in ADKPython v1.18.0Java v0.4.0

[Apigee](https://docs.cloud.google.com/apigee/docs/api-platform/get-started/what-apigee) provides a powerful [AI Gateway](https://cloud.google.com/solutions/apigee-ai), transforming how you manage and govern your generative AI model traffic. By exposing your AI model endpoint (like Agent Platform or the Gemini API) through an Apigee proxy, you immediately gain enterprise-grade capabilities:

- **Model Safety:** Implement security policies like Model Armor for threat protection.
- **Traffic Governance:** Enforce Rate Limiting and Token Limiting to manage costs and prevent abuse.
- **Performance:** Improve response times and efficiency using Semantic Caching and advanced model routing.
- **Monitoring & Visibility:** Get granular monitoring, analysis, and auditing of all your AI requests.

The `ApigeeLLM` wrapper is designed for use with Agent Platform and the Gemini API (generateContent). We are continually expanding support for other models and interfaces. For OpenAI compatible models, including self-hosted or other providers, use the `CompletionsHTTPClient` to route traffic through your Apigee proxy.

## Implementation example

Integrate Apigee's governance into your agent's workflow by instantiating the `ApigeeLlm` wrapper object and pass it to an `LlmAgent` or other agent type.

```python
from google.adk.agents import LlmAgent
from google.adk.models.apigee_llm import ApigeeLlm

# Instantiate the ApigeeLlm wrapper
model = ApigeeLlm(
    # Specify the Apigee route to your model. For more info, check out the ApigeeLlm documentation (https://github.com/google/adk-python/tree/main/contributing/samples/models/hello_world_apigeellm).
    model="apigee/gemini-flash-latest",
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

```java
import com.google.adk.agents.LlmAgent;
import com.google.adk.models.ApigeeLlm;
import com.google.common.collect.ImmutableMap;

ApigeeLlm apigeeLlm =
        ApigeeLlm.builder()
            .modelName("apigee/gemini-flash-latest") // Specify the Apigee route to your model. For more info, check out the ApigeeLlm documentation
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

With this configuration, every API call from your agent will be routed through Apigee first, where all necessary policies (security, rate limiting, logging) are executed before the request is securely forwarded to the underlying AI model endpoint. For a full code example using the Apigee proxy, see [Hello World Apigee LLM](https://github.com/google/adk-python/tree/main/contributing/samples/models/hello_world_apigeellm).

## Compatibility with OpenAI

The `CompletionsHTTPClient` is a generic HTTP client designed for compatibility with the OpenAI API format. It allows you to route requests through proxies (such as Apigee) that expect standard OpenAI-compatible `/chat/completions` endpoints, rather than native Gemini or Vertex AI protocols. This client handles:

- **Payload construction**: Converts LlmRequest objects into the format required by OpenAI-compatible APIs.
- **Response handling**: Manages streaming and non-streaming responses from the proxy.
- **Reliability**: Uses `tenacity` for built-in retry logic.
- **Normalization**: Parses responses and streaming chunks into the standard format expected by the rest of the ADK framework.

### Implementation example

```python
import asyncio
from google.adk.models.apigee_llm import CompletionsHTTPClient
from google.adk.models.llm_request import LlmRequest
from google.genai import types

async def test_client():
    # 1. Initialize the client
    client = CompletionsHTTPClient(
        base_url="https://your-apigee-proxy-url.com/v1",
        headers={"Authorization": "Bearer YOUR_API_KEY"}
    )

    # 2. Construct a minimal request
    request = LlmRequest(
        model="gpt-4o",  # Replace with your target model ID
        contents=[types.Content(role="user", parts=[types.Part.from_text(text="Hello!")])]
    )

    # 3. Execute a non-streaming generation
    async for response in client.generate_content_async(request, stream=False):
        print(f"Response: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_client())
```
