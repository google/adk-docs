# Apigee AI Gateway for ADK agents

Supported in ADKPython v1.18.0Java v0.4.0

[Apigee](https://docs.cloud.google.com/apigee/docs/api-platform/get-started/what-apigee) provides a powerful [AI Gateway](https://cloud.google.com/solutions/apigee-ai), transforming how you manage and govern your generative AI model traffic. By exposing your AI model endpoint (like Vertex AI or the Gemini API) through an Apigee proxy, you immediately gain enterprise-grade capabilities:

- **Model Safety:** Implement security policies like Model Armor for threat protection.
- **Traffic Governance:** Enforce Rate Limiting and Token Limiting to manage costs and prevent abuse.
- **Performance:** Improve response times and efficiency using Semantic Caching and advanced model routing.
- **Monitoring & Visibility:** Get granular monitoring, analysis, and auditing of all your AI requests.

Note

The `ApigeeLLM` wrapper is currently designed for use with Vertex AI and the Gemini API (generateContent). We are continually expanding support for other models and interfaces.

## Example implementation

Integrate Apigee's governance into your agent's workflow by instantiating the `ApigeeLlm` wrapper object and pass it to an `LlmAgent` or other agent type.

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

With this configuration, every API call from your agent will be routed through Apigee first, where all necessary policies (security, rate limiting, logging) are executed before the request is securely forwarded to the underlying AI model endpoint. For a full code example using the Apigee proxy, see [Hello World Apigee LLM](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world_apigeellm).
