---
catalog_title: Bifrost
catalog_description: Route LLM requests through a self-hosted, open-source AI gateway
catalog_icon: /integrations/assets/bifrost.png
catalog_tags: ["connectors"]
---

# Bifrost gateway for ADK agents

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Bifrost](https://github.com/maximhq/bifrost) is an open-source (Apache-2.0) AI
gateway written in Go that you run on your own infrastructure. It provides an
OpenAI-compatible API across providers such as Gemini, Anthropic, OpenAI,
Bedrock, Mistral, and Ollama, with fallbacks, load balancing, virtual keys with
budgets and rate limits, and semantic caching.

Since Bifrost exposes an OpenAI-compatible endpoint, you can connect ADK agents
to it using the [LiteLLM](/agents/models/litellm/) model connector.

## Use cases

- **Multi-provider routing**: Switch the model behind an agent by changing a
  `provider/model` string, with provider API keys kept on the gateway
- **Budgets and rate limits**: Give each agent or team its own virtual key with
  spending limits and token or request rate limits
- **Reliability**: Fail over to backup providers and balance traffic across
  provider API keys
- **Usage visibility**: Inspect requests in the gateway's built-in logs, or
  export metrics and traces with Prometheus and OpenTelemetry

## Prerequisites

- A Bifrost gateway with at least one provider configured (see Setup)
- ADK and LiteLLM installed in your environment

## Setup

Install dependencies:

```bash
pip install google-adk "litellm>=1.84"
```

Start Bifrost:

```bash
npx -y @maximhq/bifrost
```

You can also run it with Docker (`docker run -p 8080:8080 maximhq/bifrost`).
These unversioned commands are meant for local evaluation. For a shared
deployment, pin a version and enable authentication as described in the
[Bifrost setup guide](https://docs.getbifrost.ai/quickstart/gateway/setting-up).

Open the Bifrost web UI at `http://localhost:8080`, go to **Model Providers**,
select a provider (for example, Google Gemini), and add your provider API key.
Provider keys stay on the gateway, so your agent only needs the gateway URL and
a Bifrost virtual key.

To apply budgets, rate limits, or model restrictions, create a
[virtual key](https://docs.getbifrost.ai/features/governance/virtual-keys) in
Bifrost and export it:

```bash
export BIFROST_VIRTUAL_KEY="sk-bf-..."
```

## Use with agent

Use the `LiteLlm` wrapper with `api_base` pointing to Bifrost's
OpenAI-compatible endpoint. The `model` parameter uses the `openai/` prefix,
which tells LiteLLM to send an OpenAI-format request, followed by the Bifrost
model ID in `provider/model` form.

```python
import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

# "gemini/gemini-flash-latest" is the Bifrost model ID (provider/model).
root_agent = Agent(
    model=LiteLlm(
        model="openai/gemini/gemini-flash-latest",
        api_base="http://localhost:8080/v1",
        api_key=os.environ["BIFROST_VIRTUAL_KEY"],
    ),
    name="bifrost_agent",
    instruction="You are a helpful assistant.",
)
```

To route the agent to a different provider, change the Bifrost model ID, for
example to `openai/anthropic/claude-sonnet-4-6`. The provider must be configured
in Bifrost.

## Tips

- LiteLLM sends `api_key` as a Bearer token, which Bifrost reads as the virtual
  key. If your gateway does not enforce virtual keys, LiteLLM still requires a
  non-empty `api_key`, so set it to any string.
- If authentication is enabled on inference requests, the `Authorization` header
  carries those credentials. Pass the virtual key in the `x-bf-vk` header
  instead, for example with
  `extra_headers={"x-bf-vk": os.environ["BIFROST_VIRTUAL_KEY"]}`.
- Behind a proxy or on a remote host, replace `localhost:8080` with your gateway
  address.
- The gateway's `GET /v1/models` endpoint lists the model IDs it can serve.

## Resources

- [Bifrost documentation](https://docs.getbifrost.ai/): Setup, provider
  configuration, and gateway features.
- [Bifrost virtual keys](https://docs.getbifrost.ai/features/governance/virtual-keys):
  Budgets, rate limits, and access control per key.
- [Bifrost GitHub repository](https://github.com/maximhq/bifrost): Source code
  and releases.
- [LiteLLM model connector](/agents/models/litellm/): Documentation for the
  LiteLLM wrapper used to connect ADK agents to compatible endpoints.
