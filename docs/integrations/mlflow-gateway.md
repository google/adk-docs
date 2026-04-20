---
catalog_title: MLflow AI Gateway
catalog_description: Route LLM requests through MLflow AI Gateway for unified multi-provider access with built-in governance
catalog_icon: /integrations/assets/mlflow.png
catalog_tags: ["model provider"]
---

# MLflow AI Gateway for ADK agents

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[MLflow AI Gateway](https://mlflow.org/docs/latest/genai/governance/ai-gateway/) is a database-backed LLM proxy built into the MLflow tracking server (MLflow ≥ 3.0). It provides a unified OpenAI-compatible API across dozens of providers — OpenAI, Anthropic, Gemini, Mistral, Bedrock, Ollama, and more — with built-in secrets management, fallback/retry, traffic splitting, and budget tracking, all configured through the MLflow UI.

Since MLflow AI Gateway exposes an OpenAI-compatible endpoint, you can connect ADK agents to it using the [LiteLLM](/agents/models/litellm/) model connector.

## Use cases

- **Multi-provider routing** — switch LLM providers without changing agent code
- **Secrets management** — provider API keys stored encrypted on the server; your application sends no provider keys
- **Fallback & retry** — automatic failover to backup models on failure
- **Budget tracking** — per-endpoint or per-user token budgets
- **Traffic splitting** — route percentages of requests to different models for A/B testing
- **Usage tracing** — every call logged as an MLflow trace automatically

## Prerequisites

- MLflow version 3.0 or newer
- A running MLflow tracking server with at least one gateway endpoint configured
- Google ADK and LiteLLM installed in your environment

## Install dependencies

```bash
pip install mlflow[genai] google-adk litellm
```

## Start the MLflow server

```bash
mlflow server --host 127.0.0.1 --port 5000
```

The MLflow UI will be available at `http://localhost:5000`.

## Create a gateway endpoint

Navigate to the MLflow UI at `http://localhost:5000`, then go to **AI Gateway → Create Endpoint**. Select a provider (e.g., OpenAI) and model (e.g., `gpt-4o-mini`), and enter your provider API key — it is stored encrypted on the server.

![MLflow AI Gateway — Create Endpoint](assets/mlflow-gateway-create-endpoint.png)

See the [MLflow AI Gateway documentation](https://mlflow.org/docs/latest/genai/governance/ai-gateway/endpoints/) for details on endpoint configuration.

## Example: Connect an ADK agent to MLflow AI Gateway

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

You can swap the underlying LLM provider at any time by reconfiguring the gateway endpoint in the MLflow UI — no code changes required in your ADK agent.

## Tips

- The `api_key` parameter is required by LiteLLM but not validated by the gateway — set it to any non-empty string.
- Behind a proxy or on a remote host, replace `localhost:5000` with your server address.
- Combine with [MLflow Tracing](/integrations/mlflow/) for end-to-end observability of your ADK agents.

## Resources

- [MLflow AI Gateway Documentation](https://mlflow.org/docs/latest/genai/governance/ai-gateway/): Official documentation for MLflow AI Gateway covering endpoint management, query APIs, and gateway features.
- [MLflow Tracing for ADK](/integrations/mlflow/): Set up observability for your ADK agents with MLflow Tracing.
- [LiteLLM model connector](/agents/models/litellm/): Documentation for the LiteLLM wrapper used to connect ADK agents to OpenAI-compatible endpoints.
