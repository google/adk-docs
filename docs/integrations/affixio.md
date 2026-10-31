---
catalog_title: AffixIO
author: AffixIO
catalog_description: Verify agent tool permissions and preserve decision evidence before an ADK tool executes
catalog_tags: ["security", "authorization", "agent-identity"]
---

# AffixIO authorization guard

[AffixIO ADK](https://pypi.org/project/affixio-adk/) adds a fail-closed authorization check around Python functions exposed as Google ADK tools. An explicit `allow` decision is required before the function runs. `deny`, `review`, malformed decisions, and authorization failures do not execute the tool.

## Use cases

- **Tool authorization**: Check whether an agent may call a sensitive function before execution.
- **Review boundaries**: Stop `review` decisions until a separate approval process completes.
- **Decision evidence**: Keep the returned decision and audit evidence with the host application’s run record.

## Prerequisites

- Python 3.10 or later
- An AffixIO API key
- An ADK agent project

## Installation

```bash
pip install "affixio-adk[google]"
```

## Use with an agent

```python
import os
from google.adk.agents import LlmAgent
from affixio_adk import AffixIOAuthorizer

authorizer = AffixIOAuthorizer(
    os.environ["AFFIXIO_API_KEY"],
    agent_id="my-agent",
)

@authorizer.tool
def lookup_order(order_id: str) -> dict[str, str]:
    return {"order_id": order_id, "status": "ready"}

root_agent = LlmAgent(
    name="verified_agent",
    model="gemini-2.5-flash",
    instruction="Use lookup_order only for order questions.",
    tools=[lookup_order],
)
```

The wrapper is an ordinary Python callable, so it can be registered wherever ADK accepts a function tool. It does not send private prompts or operator identity to AffixIO. Applications should still apply their own input validation and secrets management.

## Decision behaviour

| Decision | Result |
| --- | --- |
| `allow` | The tool may execute. |
| `deny` | The tool is blocked. |
| `review` | The tool is blocked pending separate approval. |
| API timeout or error | The tool is blocked by default. |

## Resources

- [AffixIO ADK source](https://github.com/AffixIO/affixio-adk)
- [AffixIO documentation](https://www.affix-io.com/docs/)
- [AffixIO security](https://www.affix-io.com/security/)
