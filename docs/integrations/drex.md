---
catalog_title: Drex
catalog_description: Block model and tool calls from a Drex probability
catalog_icon: /integrations/assets/drex.svg
---

# Block model and tool calls with Drex

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Drex](https://console.nace.ai/docs) returns a probability for a yes or no
question, a choice, or a score. The
[adk-nace](https://github.com/nace-ai/adk-nace) plugin is published by Nace, not
by the ADK project. It calls `NaceClient.system_one` from
[nace-sdk](https://pypi.org/project/nace-sdk/) 0.4.0 and blocks the call when
your `fail_if` function returns true.

## Use cases

- **Block a model call**: Check the request text before the model runs, and
  return a refusal when the probability is at or above your threshold.
- **Skip a tool call**: Check the tool name and arguments before the tool runs,
  and return a refusal dict instead of executing the tool.

## Prerequisites

- Python 3.11 or later
- A [Nace API key](https://console.nace.ai/dashboard/api-keys)
- Model credentials, if a check allows the call and the agent then calls the model

## Installation

`adk-nace` is not on PyPI. Install it from GitHub:

```bash
pip install "adk-nace[adk] @ git+https://github.com/nace-ai/adk-nace.git"
```

## Set the API key

`open_client()` reads `NACE_API_KEY`. Do not pass the key in code.

```env title=".env"
NACE_API_KEY="YOUR_API_KEY"
```

## Register the plugin

Register `DrexPlugin` once on the `App`. The runner then applies it to every
model call and tool call.

```python
from google.adk.agents import Agent
from google.adk.apps import App
from nace_sdk import Noul

from adk_nace import open_client
from adk_nace.plugin import DrexPlugin


def block_refund(name: str, answer) -> bool:
    return answer.noul >= 0.5


root_agent = Agent(
    name="billing",
    model="gemini-flash-latest",
    description="Answers billing questions.",
    instruction="Answer billing questions. Do not issue a refund yourself.",
)

app = App(
    name="billing",
    root_agent=root_agent,
    plugins=[
        DrexPlugin(
            open_client(),
            {
                "refund": Noul(
                    instructions="Is the customer asking for a refund?",
                ),
            },
            block_refund,
        )
    ],
)
```

The plugin passes `model="drex-v2.0"` unless you set `model`. `answer.noul` is
the probability of a yes answer, not a boolean. `0.5` is your threshold.

`before_model_callback` returns an `LlmResponse` to block and `None` to allow.
The plugin also checks the model response and can replace it. `before_tool_callback`
returns a dict to skip the tool and `None` to allow it.
An API error is raised. The plugin does not treat that error as an allow.

Pass a string for `instructions`.

Images require `model="drex-max"`. With any other model, the plugin raises
`CheckError` before the request. If a request with images reaches `drex-v2.0`,
the API returns HTTP 422.

`drex-max` accepts at most 16 questions and 8 images. `drex-v2.0` accepts at
most 512 questions and no images.

A blocked check returns before the model call, so that path does not need model
credentials. An allowed check continues to the model. Configure those
credentials as in the
[ADK quickstart](../get-started/index.md).

## Resources

- [adk-nace](https://github.com/nace-ai/adk-nace)
- [nace-sdk on PyPI](https://pypi.org/project/nace-sdk/)
- [Drex documentation](https://console.nace.ai/docs)
