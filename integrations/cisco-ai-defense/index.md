# Cisco AI Defense plugin for ADK

Supported in ADKPython

[Cisco AI Defense](https://www.cisco.com/site/us/en/products/security/ai-defense/index.html) is an enterprise AI security platform that provides runtime guardrails to protect against threats like prompt injection, data leakage, and harmful content. The [ADK plugin](https://github.com/cisco-ai-defense/ai-defense-google-adk) integrates these guardrails directly into the ADK Runner lifecycle: it inspects prompts, model responses, and tool calls, then allows or blocks them based on configurable security policies.

## Use cases

- **Runtime protection for model calls**: Inspect user prompts before model calls and model outputs after generation, then allow or block based on policy (`monitor` or `enforce`).
- **Tool and MCP call inspection**: Inspect tool call requests before execution and tool responses after execution, and block unsafe tool behavior in `enforce` mode with clear metadata.
- **Auditable decision trace and alerts**: Capture decision context (action, severity, classifications, request_id/event_id) and optionally trigger an `on_violation` callback for monitoring and incident response.

## Prerequisites

- [Cisco AI Defense](https://www.cisco.com/site/us/en/products/security/ai-defense/index.html) account and API key
- Python >= 3.10
- [ADK](https://adk.dev) >= 1.0.0

## Installation

```bash
pip install cisco-aidefense-google-adk
```

Set the `AI_DEFENSE_API_KEY` environment variable (and `AI_DEFENSE_MCP_API_KEY` for tool inspection).

## Use with agent

### Quickstart

Add Cisco AI Defense to any ADK agent with a single line:

```python
from aidefense_google_adk import defend

agent = defend(agent, mode="enforce")
```

Or get a plugin for the entire app:

```python
from aidefense_google_adk import defend

plugin = defend(mode="enforce")
app = App(name="my_app", root_agent=agent, plugins=[plugin])
```

### Global plugin

Use `CiscoAIDefensePlugin` to apply inspection globally to all agents in a Runner:

```python
from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from aidefense_google_adk import CiscoAIDefensePlugin

agent = LlmAgent(
    model="gemini-flash-latest",
    name="assistant",
    instruction="You are a helpful assistant.",
)

app = App(
    name="my_app",
    root_agent=agent,
    plugins=[
        CiscoAIDefensePlugin(mode="enforce"),
    ],
)
runner = Runner(app=app, session_service=InMemorySessionService())
```

### Per-agent callbacks

Use `make_aidefense_callbacks` to wire inspection into a specific agent:

```python
from google.adk.agents import LlmAgent
from aidefense_google_adk import make_aidefense_callbacks

cbs = make_aidefense_callbacks(mode="enforce")

agent = LlmAgent(
    model="gemini-flash-latest",
    name="assistant",
    instruction="You are a helpful assistant.",
)
cbs.apply_to(agent)  # wires all 4 callbacks
```

## Modes

The plugin supports three operating modes:

| Mode      | Behavior                                                          |
| --------- | ----------------------------------------------------------------- |
| `monitor` | Inspect all traffic, log violations, never block (default)        |
| `enforce` | Inspect all traffic, block requests/responses that violate policy |
| `off`     | Skip inspection entirely                                          |

Modes can be set globally or per-channel:

```python
CiscoAIDefensePlugin(
    mode="monitor",      # default for both
    llm_mode="enforce",  # override for LLM only
    mcp_mode="off",      # override for tools only
)
```

## Violation callback

Use the `on_violation` callback to receive notifications for every violation in both `monitor` and `enforce` modes:

```python
def handle_violation(result):
    print(f"Violation: {result.action} / {result.severity}")

CiscoAIDefensePlugin(
    mode="monitor",
    on_violation=handle_violation,
)
```

## Retry and fail-open support

For automatic retry with exponential backoff, fail-open/fail-closed semantics, and structured `Decision` objects, use the `AgentsecPlugin` variant:

```python
from aidefense_google_adk import AgentsecPlugin

app = App(
    name="my_app",
    root_agent=agent,
    plugins=[
        AgentsecPlugin(
            mode="enforce",
            fail_open=True,
            retry_total=3,
            retry_backoff=0.5,
        ),
    ],
)
```

Or at the per-agent level:

```python
from aidefense_google_adk import make_agentsec_callbacks

cbs = make_agentsec_callbacks(mode="enforce", fail_open=True)
cbs.apply_to(agent)
```

## Additional resources

- [GitHub Repository](https://github.com/cisco-ai-defense/ai-defense-google-adk)
- [PyPI Package](https://pypi.org/project/cisco-aidefense-google-adk/)
- [Cisco AI Defense](https://www.cisco.com/site/us/en/products/security/ai-defense/index.html)
- [cisco-aidefense-sdk on PyPI](https://pypi.org/project/cisco-aidefense-sdk/)
