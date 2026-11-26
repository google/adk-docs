---
catalog_title: Donkey Development Kit
catalog_description: Govern agents, model calls, and MCP tools with MuleSoft Agent Fabric
catalog_icon: /integrations/assets/donkey-kit.png
catalog_tags: ["connectors"]
---

# Donkey Development Kit connector for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [Donkey Development Kit](https://docs.donkey-kit.dev) (DDK, PyPI package
`donkey-kit`) is an open-source Python SDK that puts ADK agents under MuleSoft
Agent Fabric governance. It covers the agent's model calls, the MCP tools it
calls, and the agent itself. Policies such as token budgets, PII detection,
content safety, model routing, tool access, and the agent kill switch run on
MuleSoft Omni Gateway. DDK makes those policies visible to your agent code.

For ADK, DDK returns ADK's own classes, already pointed at the gateway: a
`LiteLlm` or native `Gemini` model for an LLM proxy, an `McpToolset` for each
governed MCP server, and a plugin for approval-gated tools. You pass them to
`Agent(...)` as you would any other ADK model, toolset, or plugin.

## Use cases

- **Governed model access**: Send every agent model call through one gateway
  that enforces auth, token budgets, and content policies, with no provider
  keys in the agent process.
- **Governed MCP tools**: Discover MCP servers from Anypoint Exchange and bind
  only the ones the gateway governs, so gateway policies and access profiles
  apply to every tool call.
- **Typed policy refusals**: Handle a gateway block as a specific exception,
  such as `PIIDetected`, `TokenBudgetExceeded`, or `AgentKilled` from the
  kill switch, instead of a generic HTTP error.
- **Human approval for tools**: Pause approval-gated tools with ADK tool
  confirmation and resume after a reviewer decides.
- **Agent registration**: Register the agent and its tools in Anypoint
  Exchange from CI with `donkey scan` and `donkey publish`, and expose it to
  other agents over A2A.
- **Per-call gateway data in callbacks**: Read the served model, routing
  decision, and token usage for each call in an `after_model_callback`.
- **Offline failure testing**: Run the agent against a local simulator that
  replays real gateway rejections on demand.

## Prerequisites

- Python 3.10 or later and ADK 2.4 or later
- An LLM proxy on MuleSoft Omni Gateway, with its base URL and a consumer
  `client_id` and `client_secret`. To try the integration without a gateway,
  use the [local simulator](#test-without-a-gateway).
- For MCP tool discovery, an Anypoint connected app with access to Exchange in
  your organization

## Installation

```bash
pip install "donkey-kit[adk,mcp]"
```

The `adk` extra installs `google-adk` and `litellm[mcp]`. The `mcp` extra
installs the MCP client used for governed tools.

## Use with agent

Set the proxy connection in the environment. The base URL has no `/v1` suffix:

```bash
export DONKEY_LLM_PROXY_URL="https://<gateway-host>/<proxy-base-path>/"
export DONKEY_LLM_PROXY_CLIENT_ID="<consumer client id>"
export DONKEY_LLM_PROXY_CLIENT_SECRET="<consumer client secret>"
```

=== "OpenAI-format proxy (LiteLlm)"

    The `model()` factory returns ADK's `LiteLlm` with the proxy's base URL and
    auth headers set, and the `openai/` model prefix added for LiteLLM.

    ```python
    from google.adk.agents import Agent
    from donkey_kit.integrations.adk import model

    root_agent = Agent(
        model=model("gemini-flash-latest"),
        name="governed_agent",
        instruction="You are a helpful assistant.",
    )
    ```

=== "Gemini-format proxy (Gemini)"

    The `gemini()` factory returns ADK's native `Gemini` model, bound to a
    proxy that exposes the Gemini API. Pass the bare model ID.

    ```python
    from google.adk.agents import Agent
    from donkey_kit.integrations.adk import gemini

    root_agent = Agent(
        model=gemini("gemini-flash-latest"),
        name="governed_agent",
        instruction="You are a helpful assistant.",
    )
    ```

    The `gemini()` factory needs ADK 2.4 or later, the first release where
    `Gemini` accepts `client_kwargs`.

Both factories return a subclass of the ADK class that carries DDK's per-call
record into ADK callbacks. To build the model yourself, use the native
constructor with DDK's connection arguments:

```python
from donkey_kit import Donkey
from google.adk.models.lite_llm import LiteLlm

async with Donkey.from_env() as donkey:
    llm = LiteLlm(
        model="openai/gemini-flash-latest",
        **donkey.adk.connection_kwargs(),
    )
```

## Available methods

The `donkey_kit.integrations.adk` module provides:

Function | Description
-------- | -----------
`model(model)` | Returns a `LiteLlm` bound to an OpenAI-format proxy.
`gemini(model, base_url=None)` | Returns a native `Gemini` bound to a Gemini-format proxy.
`last_call_bridged(model_class)` | Wraps your own model class so callbacks can read the per-call record.
`approval_plugin()` | Returns an ADK plugin that pauses approval-gated tools with ADK tool confirmation.
`pending_approvals(events)` | Returns the paused tool calls among a run's events.
`approve(approval, by)` | Returns the approval with the ADK confirmation part that resumes the tool.
`reject(approval, by, message=None)` | Returns the approval with the ADK confirmation part that refuses the tool.

A `Donkey` instance's `donkey.adk` attribute provides `model()` and `gemini()`
too, plus:

Method | Description
------ | -----------
`connection_kwargs()` | Returns the keyword arguments for your own `LiteLlm(...)`.
`gemini_connection_kwargs()` | Returns the keyword arguments for your own `Gemini(...)`.

A `ToolSet` from `donkey.tools.discover()` provides `adk()`, which returns one
`McpToolset` per governed MCP server.

## Configuration

### Bind governed MCP tools

The `donkey.tools.discover()` method finds MCP servers in Anypoint Exchange
that the gateway governs. The `adk()` method binds them as ADK `McpToolset`
objects that send your gateway credential on every tool call. Binding refuses
any server the gateway does not front with `UngovernedMcpServer`, before a
connection opens.

```python
from donkey_kit import Donkey
from google.adk.agents import Agent

async with Donkey.from_env() as donkey:
    tools = await donkey.tools.discover(tags=["crm"])
    toolsets = await tools.filter(deny=["delete_*"]).adk()

    root_agent = Agent(
        model=donkey.adk.model("gemini-flash-latest"),
        name="governed_agent",
        instruction="You are a helpful assistant.",
        tools=toolsets,
    )
```

Discovery reads Exchange with the Anypoint connected app set in
`ANYPOINT_CLIENT_ID`, `ANYPOINT_CLIENT_SECRET`, and `ANYPOINT_ORG_ID`. Close
each toolset with `await toolset.close()` when the agent is done.

### Pause tools for approval

Mark a tool with `@donkey.tool(approval="required")` and add the plugin from
`approval_plugin()` to your `App`. The run pauses the tool with ADK tool
confirmation, and `approve()` or `reject()` builds the message that resumes it:

```python
from donkey_kit import Donkey
from donkey_kit.integrations.adk import approval_plugin, approve, pending_approvals
from google.adk.agents import Agent
from google.adk.apps import App
from google.genai import types

donkey = Donkey.from_env()

@donkey.tool(approval="required", risk="financial")
def issue_refund(ticket_id: str, amount: float) -> str:
    """Refund a support ticket."""
    return f"refunded {ticket_id}"

root_agent = Agent(
    model=donkey.adk.model("gemini-flash-latest"),
    name="refunds",
    instruction="You handle refund requests.",
    tools=[issue_refund],
)
app = App(name="refunds", root_agent=root_agent, plugins=[approval_plugin()])

# events: the events from a runner.run_async(...) call on this app.
# Show the paused calls to a reviewer, then send the answer as the next message:
approvals = pending_approvals(events)
decided = [approve(a, by="reviewer@example.com") for a in approvals]
resume = types.Content(role="user", parts=[a.native for a in decided])
```

### Read gateway data in a callback

ADK's `Runner` makes the model call in its own task, so read the per-call
record in an `after_model_callback`:

```python
from donkey_kit import Donkey
from google.adk.agents import Agent

donkey = Donkey.from_env()

def record_usage(callback_context, llm_response):
    call = donkey.last_call
    print(call.served_model, call.input_tokens, call.output_tokens)
    return None  # keep the model's response

root_agent = Agent(
    model=donkey.adk.model("gemini-flash-latest"),
    name="governed_agent",
    instruction="You are a helpful assistant.",
    after_model_callback=record_usage,
)
```

### Handle gateway refusals

On the `model()` path, a gateway refusal raised inside `donkey.run()` arrives
as a typed DDK error. LiteLLM's original error is kept on `framework_error`.

```python
from donkey_kit import AgentKilled, PIIDetected, TokenBudgetExceeded

async with donkey.run():
    try:
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=message
        ):
            ...
    except PIIDetected:
        ...  # ask the user to remove personal data
    except TokenBudgetExceeded as err:
        ...  # back off until the budget resets
    except AgentKilled:
        ...  # the agent kill switch is on: stop the agent
```

### Test without a gateway

The `donkey mock` command runs a local server that replays captured gateway
responses. Set the model to `donkey-sim/<shape>`, for example
`donkey-sim/pii-detected`, to trigger a specific refusal.

```bash
pip install "donkey-kit[adk,cli,local]"
donkey mock --port 8080
export DONKEY_LLM_PROXY_URL="http://localhost:8080/"
export DONKEY_LLM_PROXY_CLIENT_ID="local"
export DONKEY_LLM_PROXY_CLIENT_SECRET="local"
```

## Additional resources

- [DDK documentation for ADK](https://docs.donkey-kit.dev/frameworks/adk)
- [Runnable ADK example](https://github.com/Donkey-Development-Kit/donkey-development-kit/tree/main/python/examples/adk)
- [Governed MCP tool binding](https://docs.donkey-kit.dev/tool-access/binding)
- [Human-in-the-loop approvals](https://docs.donkey-kit.dev/hitl)
- [Agent registration](https://docs.donkey-kit.dev/publishing)
- [A2A agents](https://docs.donkey-kit.dev/a2a)
- [Error reference](https://docs.donkey-kit.dev/errors)
- [Local simulator](https://docs.donkey-kit.dev/simulator)
- [GitHub repository and issues](https://github.com/Donkey-Development-Kit/donkey-development-kit)
- [donkey-kit on PyPI](https://pypi.org/project/donkey-kit/)
