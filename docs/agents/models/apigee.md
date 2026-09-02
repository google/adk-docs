# Apigee AI Gateway for ADK agents

<div class="language-support-tag">
   <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.18.0</span><span class="lst-java">Java v0.4.0</span>
</div>

[Apigee](https://docs.cloud.google.com/apigee/docs/api-platform/get-started/what-apigee)
provides a powerful [AI Gateway](https://cloud.google.com/solutions/apigee-ai),
transforming how you manage and govern your generative AI model traffic. By
exposing your AI model endpoint (like Agent Platform or the Gemini API) through an
Apigee proxy, you immediately gain enterprise-grade capabilities:

- **Model Safety:** Implement security policies like Model Armor for threat protection.

- **Traffic Governance:** Enforce Rate Limiting and Token Limiting to manage costs and prevent abuse.

- **Performance:** Improve response times and efficiency using Semantic Caching and advanced model routing.

- **Monitoring & Visibility:** Get granular monitoring, analysis, and auditing of all your AI requests.

   The `ApigeeLlm` wrapper is designed for use with Agent Platform
   and the Gemini API (generateContent). We are continually expanding support for
   other models and interfaces. For OpenAI compatible models, including self-hosted or 
   other providers, use the `CompletionsHTTPClient` to route traffic through your Apigee proxy.

## Implementation example

Integrate Apigee's governance into your agent's workflow by instantiating the
`ApigeeLlm` wrapper object and pass it to an `LlmAgent` or other agent type.

=== "Python"

    ```python
    --8<-- "examples/inline/python/agents/models/apigee/001-implementation-example.py"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/agents/models/apigee/002-implementation-example.java"
    ```

With this configuration, every API call from your agent will be routed through
Apigee first, where all necessary policies (security, rate limiting, logging)
are executed before the request is securely forwarded to the underlying AI model
endpoint. For a full code example using the Apigee proxy, see
[Hello World Apigee LLM](https://github.com/google/adk-python/tree/main/contributing/samples/models/hello_world_apigeellm).

## Compatibility with OpenAI

The `CompletionsHTTPClient` is a generic HTTP client designed for compatibility with the OpenAI API format. It allows you to route requests through proxies (such as Apigee) that expect standard OpenAI-compatible `/chat/completions` endpoints, rather than native Gemini or Vertex AI protocols. This client handles:

- **Payload construction**: Converts LlmRequest objects into the format required by OpenAI-compatible APIs.
- **Response handling**: Manages streaming and non-streaming responses from the proxy.
- **Reliability**: Uses `tenacity` to retry non-streaming requests, but only when you pass `retry_options=types.HttpRetryOptions(...)` to the constructor. By default each request is attempted once, and streaming requests are never retried.
- **Normalization**: Parses responses and streaming chunks into the standard format expected by the rest of the ADK framework.

### Implementation example

```python
--8<-- "examples/inline/python/agents/models/apigee/003-implementation-example.py"
```
