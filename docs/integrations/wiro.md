---
catalog_title: Wiro AI
catalog_description: Run agents on LLMs from several providers with one API key
catalog_icon: /integrations/assets/wiro.png
catalog_tags: ["connectors"]
---

# Wiro AI model gateway for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Wiro AI](https://wiro.ai) gives access to large language models from several
providers, including Anthropic Claude, OpenAI GPT, DeepSeek, and Qwen, through
one OpenAI-compatible API at `https://llm.wiro.ai/v1`. A single Wiro project
credential works for every model, and usage is billed per token to a prepaid
Wiro wallet.

Since the gateway uses the OpenAI Chat Completions format, you can connect ADK
agents to it using the [LiteLLM](/agents/models/litellm/) model connector.

## Use cases

- **Several model providers, one credential**: Run the same agent on Claude,
  GPT, DeepSeek, or Qwen models by changing the model string.
- **Tool calling**: ADK function tools work through the gateway with models
  that support tool calling.
- **Model comparison**: Try an agent and its tools on different models without
  setting up a separate account for each provider.

## Prerequisites

- A Wiro AI project. Create one at
  [wiro.ai/panel/project/new](https://wiro.ai/panel/project/new) and copy its
  API key (and API secret, if the project uses signature authentication).
- Credit in your Wiro wallet.
- Python 3.11 or newer.

## Installation

Install ADK and LiteLLM:

```bash
pip install google-adk litellm
```

Set your project credential:

```bash
export WIRO_API_KEY="YOUR_API_KEY"
```

For a project that uses signature authentication, set the key and the secret
joined by a colon: `YOUR_API_KEY:YOUR_API_SECRET`.

## Use with agent

Use the `LiteLlm` wrapper with `api_base` pointing to the Wiro AI gateway. The
`model` parameter is `openai/` followed by a model ID from the
[Wiro AI model list](https://llm.wiro.ai/v1/models). The `openai/` prefix tells
LiteLLM to send the request in the OpenAI-compatible format.

```python
import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm


def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    return {"status": "success", "city": city, "time": "10:30 AM"}


root_agent = Agent(
    model=LiteLlm(
        model="openai/claude/sonnet-5",
        api_base="https://llm.wiro.ai/v1",
        api_key=os.environ["WIRO_API_KEY"],
    ),
    name="wiro_agent",
    instruction=(
        "You are a helpful assistant. Use the get_current_time tool when "
        "the user asks for the time in a city."
    ),
    tools=[get_current_time],
)
```

To run the same agent on another model, change the part after `openai/`, for
example `openai/deepseek/v4-1-flash`.

## Tips

- The model list at `https://llm.wiro.ai/v1/models` needs no key. Each entry
  shows the model's context length, token prices, and supported parameters,
  such as `tools`.
- The `api_key` value is sent as a Bearer token. A key alone returns
  `401 Unauthorized` for a project that uses signature authentication; send
  `YOUR_API_KEY:YOUR_API_SECRET` instead.

## Additional resources

- [Wiro AI LLM gateway documentation](https://wiro.ai/docs/completions-api):
  Base URL, authentication, and the supported OpenAI-compatible routes.
- [Wiro AI model list](https://llm.wiro.ai/v1/models): Model IDs, context
  lengths, and prices.
- [LiteLLM model connector](/agents/models/litellm/): Documentation for the
  LiteLLM wrapper used to connect ADK agents to OpenAI-compatible endpoints.
