# MLflow AI Gateway for ADK agents

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[MLflow AI Gateway](https://mlflow.org/docs/latest/genai/governance/ai-gateway/) is a database-backed LLM proxy built into the MLflow tracking server (MLflow ≥ 3.0). It provides a unified OpenAI-compatible API across dozens of providers — OpenAI, Anthropic, Gemini, Mistral, Bedrock, Ollama, and more — with built-in secrets management, fallback/retry, traffic splitting, and budget tracking, all configured through the MLflow UI.

Since MLflow AI Gateway exposes an OpenAI-compatible endpoint, you can connect ADK agents to it using the [LiteLLM](/agents/models/litellm/) wrapper.

## Setup

1. **Install MLflow and start the server:**

    ```bash
    pip install mlflow[genai]
    mlflow server --host 127.0.0.1 --port 5000
    ```

2. **Create a gateway endpoint** in the MLflow UI at `http://localhost:5000`. Navigate to **AI Gateway → Create Endpoint**, select a provider and model, and enter your provider API key (stored encrypted on the server). See the [MLflow AI Gateway documentation](https://mlflow.org/docs/latest/genai/governance/ai-gateway/endpoints/) for details.

3. **Install LiteLLM:**

    ```bash
    pip install litellm
    ```

## Example implementation

Use the `LiteLlm` wrapper with `api_base` pointing to the MLflow Gateway's OpenAI-compatible endpoint. The `model` parameter should use the `openai/` prefix followed by your gateway endpoint name.

```python
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# Point to MLflow AI Gateway's OpenAI-compatible endpoint.
# "my-chat-endpoint" is the endpoint name you created in the MLflow UI.
agent = LlmAgent(
    model=LiteLlm(
        model="openai/my-chat-endpoint",
        api_base="http://localhost:5000/gateway/openai/v1",
        api_key="unused",  # provider keys are managed by the MLflow server
    ),
    name="gateway_agent",
    instruction="You are a helpful assistant powered by MLflow AI Gateway.",
)
```

You can swap the underlying LLM provider at any time by reconfiguring the gateway endpoint in the MLflow UI — no code changes required.

## Gateway features

These are configured in the MLflow UI and apply transparently to all requests:

- **Fallback & retry** — automatic failover to backup models on failure
- **Traffic splitting** — route percentages of traffic to different models for A/B testing
- **Budget tracking** — per-endpoint or per-user token budgets
- **Usage tracing** — every call logged as an MLflow trace automatically

## Related

- [LiteLLM model connector](/agents/models/litellm/)
- [MLflow Tracing for ADK](/integrations/mlflow/)
- [MLflow AI Gateway documentation](https://mlflow.org/docs/latest/genai/governance/ai-gateway/)
