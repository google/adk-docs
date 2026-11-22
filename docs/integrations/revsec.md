---
catalog_title: RevSec
catalog_description: Block risky tool and MCP calls and screen prompts and tool results
catalog_icon: /integrations/assets/revsec.png
catalog_tags: ["mcp"]
---

# RevSec plugin for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[RevSec](https://app.revsec.app/start?from=google-adk) is a control layer for AI
agents. It decides, before each action runs, whether the agent is allowed to
take it, and keeps a record of what each agent did. The
[adk-revsec](https://github.com/RevUp-AI/adk-revsec) plugin adds RevSec to an
ADK `App`. It checks each tool call before it runs (an MCP server's tool
against that MCP server, the agent's own tools against the agent's policies),
what the user asks before it reaches the model, and what each tool hands back
before the model reads it. The plugin covers the agent's actions (Agent
Security), the MCP servers it calls (MCP Governance) and what reaches its model
(Model Security), with no changes to the agent's code.

## Use cases

- **Stop risky actions before they run**: Block a refund above a limit, a
  delete, or a call to an MCP server that nobody approved, before the tool
  runs. The model is told why, so the agent can answer the user instead of
  failing.
- **Keep prompt injection and leaked data away from the model**: RevSec Model
  Security checks what users ask before it reaches the model, and what tools
  hand back (web pages, documents, MCP replies) before the model reads it, for
  instructions aimed at the model, secrets and personal data, along with the
  organization's own prompt rules.
- **Govern MCP servers**: Check each MCP call against that server's approval,
  policies and known vulnerabilities, and record whether it succeeded and how
  long it took.
- **Review what an agent did**: Each agent appears in the RevSec console with
  the models it uses, its tools and MCP servers, and a risk rating. Activity
  Explorer replays each session (what the user asked, each tool and MCP call,
  and what RevSec decided), and the Frameworks view shows which controls in the
  EU AI Act, ISO/IEC 42001, NIST AI RMF, SOC 2 and other frameworks the
  policies are mapped to.

## Prerequisites

- A [RevSec](https://app.revsec.app/start?from=google-adk) account and SDK key
  (the 30-day trial needs no card)
- Python >= 3.11
- [ADK](/) >= 1.18

## Installation

```bash
pip install "adk-revsec[mcp]"
```

Set the `REVSEC_API_KEY` and `REVSEC_BASE_URL` environment variables. The key
comes from the RevSec console (**Customer accounts → New key**, or
**Settings → SDK**).

## Use with agent

Add `RevSecPlugin` to the `App`. It applies to the root agent and every
sub-agent:

```python
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from adk_revsec import RevSecPlugin, revsec_mcp_toolset


def refund_order(order_id: str, amount: int) -> dict:
    """Refund an order."""
    return {"order_id": order_id, "refunded": amount}


notes = revsec_mcp_toolset("notes", command="npx", args=["-y", "@acme/notes-mcp"])

root_agent = Agent(
    name="orders_agent",
    model="gemini-flash-latest",
    instruction="Help customers with their orders.",
    tools=[refund_order, notes],
)

app = App(name="orders_app", root_agent=root_agent, plugins=[RevSecPlugin()])
runner = Runner(app=app, session_service=InMemorySessionService())
```

The first request registers the agent in RevSec. From then on, its tool calls,
prompts and tool results are checked, and the decisions show in the RevSec
console:

| When | What is checked | If RevSec stops it |
|---|---|---|
| Before the run | What the user asked | The model is not called and the request is not kept in the session; the user gets a reply saying it was blocked |
| Before each tool call | The agent's own tools, against its policies | The tool does not run; the model gets a response saying why |
| Before each MCP tool call | The call, against that MCP server | The call does not reach the server; the model gets a response saying why |
| After each tool call | What the tool handed back | The model gets a "withheld" response instead |

## Configuration

Build each MCP toolset with `revsec_mcp_toolset(name, ...)` so that RevSec
checks its calls against that server. An `McpToolset` you build yourself works
too, through `note_mcp_server(toolset, "github")`:

```python
from adk_revsec import revsec_mcp_toolset

github = revsec_mcp_toolset("github", url="https://api.githubcopilot.com/mcp/")
notes = revsec_mcp_toolset("notes", command="npx", args=["-y", "@acme/notes-mcp"])
```

The plugin takes these options:

```python
RevSecPlugin(
    agent_name="orders-desk",  # default: the root agent's name
    customer_facing=True,      # shown on the agent and used in its risk rating
    on_block="message",        # or "raise" to stop the run instead
)
```

If RevSec can't be reached, calls go ahead by default, so an outage does not
stop the agent. To block them instead, call
`revsec.mcp.configure(api_key=..., failure_mode="fail_closed")` before
creating the plugin.

## Additional resources

- [GitHub Repository](https://github.com/RevUp-AI/adk-revsec)
- [PyPI Package](https://pypi.org/project/adk-revsec/)
- [RevSec](https://app.revsec.app/start?from=google-adk)
- [revsec-sdk on PyPI](https://pypi.org/project/revsec-sdk/)
