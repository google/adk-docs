# Managed agents

Supported in ADKPython v2.4.0Preview

Managed agents let you use Google's first-party, out-of-the-box agents, backed by the Managed Agents API, from within your ADK flows. Managed agents are available through the [Gemini API](https://ai.google.dev/gemini-api/docs/agents) and [Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/managed-agents). The `ManagedAgent` class connects to a managed agent (such as the Antigravity agent) that runs in a specialized, server-side execution environment, so you get powerful built-in capabilities without managing sandboxes or writing client-side function declarations.

`ManagedAgent` implements the same `BaseAgent` contract as other ADK agents, so you can use it standalone or drop it directly into an ADK flow. It is a good fit when you want a robust, server-hosted agent with specialized built-in tools rather than building and operating that environment yourself.

## What are managed agents?

A *managed agent* is an agent whose reasoning, tools, and execution environment are hosted and operated by Google through the Managed Agents API, rather than run by your own ADK process. Instead of issuing standard `generate_content` calls, `ManagedAgent` creates server-side *interactions* and streams the results back into your ADK flow. Managed agents provide several built-in advantages:

- **First-party, out-of-the-box agents:** Connect to ready-made agents (for example, the Antigravity agent) by referencing their `agent_id`.
- **Built-in, server-side execution:** Capabilities such as web search and code execution run in a managed sandbox on the server, with no local sandbox to provision or secure.
- **No client-side function declarations:** Server-side tools are configured on the managed agent, so you don't declare or execute them locally.

## When to use managed agents vs. building your own

Managed agents and ADK agents solve different problems. Choosing between them is mostly a trade-off between out-of-the-box power and fine-grained control.

- **Managed agents** give you a powerful agent out of the box, but with limited flexibility. The toolset is predefined and server-side, the agent runs only in the managed environment, and client-side or MCP tools are not supported.
- **ADK agents** (such as [`LlmAgent`](/agents/llm-agents/)) give you fine-grained control over the model, instructions, tools (including custom function tools and MCP tools), and where execution happens.

## Prerequisites

`ManagedAgent` supports two backends. Complete the prerequisites for the backend you plan to use: obtain credentials and an `agent_id`.

### Gemini API backend

- **Authentication:** Obtain a Gemini API key and set it as the `GEMINI_API_KEY` environment variable.
- **Agent ID:** You need an `agent_id` to connect to. You can either:
  - Create a new agent by following the [Gemini API Agents documentation](https://ai.google.dev/gemini-api/docs/agents).
  - Use an out-of-the-box agent ID, such as `antigravity-preview-05-2026`, which is used in the examples below.

### Agent Platform backend

- **Authentication:** Agent Platform requires Google Cloud credentials. Follow the [Agent Platform setup instructions](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/managed-agents/create-manage#before-you-begin) to authenticate your local environment (for example, with `gcloud auth application-default login`).
- **Location:** The Managed Agents API is served only from the `global` location. `ManagedAgent` enforces a connection to `global` on the Agent Platform backend.
- **Agent ID:** As with the Gemini API, you need an `agent_id`. Create one using the [Create and manage agents guide](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/managed-agents/create-manage), or use an out-of-the-box agent ID available to your project.

## Get started

The following example creates two managed agents: one that answers questions using web search, and one that solves computational questions by running code server-side. Both run their tools in the managed environment (`environment={'type': 'remote'}`).

```python
import os
from google.adk.agents import ManagedAgent
from google.adk.tools import google_search
from google.genai import types

# Ensure you have the MANAGED_AGENT_ID and the proper environment config
_AGENT_ID = os.environ.get('MANAGED_AGENT_ID', 'antigravity-preview-05-2026')

managed_search_agent = ManagedAgent(
    name='managed_search_agent',
    description='Answers questions that need fresh, grounded information from the web.',
    agent_id=_AGENT_ID,
    environment={'type': 'remote'},
    tools=[google_search],
)

# A managed code execution agent using raw types.Tool
managed_code_execution_agent = ManagedAgent(
    name='managed_code_execution_agent',
    description='Solves computational questions by running code server-side.',
    agent_id=_AGENT_ID,
    environment={'type': 'remote'},
    tools=[types.Tool(code_execution=types.ToolCodeExecution())],
)
```

## How it works

When you invoke a `ManagedAgent`, ADK sends your request to the managed agent via the [Interactions API](https://ai.google.dev/gemini-api/docs/interactions-overview) and streams the results, both partial and final, back into your ADK flow in real time. The reasoning, tools, and execution all run in Google's managed environment rather than in your ADK process.

How `ManagedAgent` maps to the Managed Agents API

An ADK `ManagedAgent` does not create or register a new managed agent resource. It connects to an agent that already exists on the backend (the one named by `agent_id`) and applies its configuration (such as `tools` and `environment`) as per-interaction overrides at runtime. In Managed Agents API terms, ADK works entirely on the *data plane* (the Interactions API) and leaves the *control plane* (the Agents API, which creates and manages agent resources) untouched. For how these two planes differ, see the [Managed Agents API system architecture](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/managed-agents).

### Local session vs. remote state

`ManagedAgent` keeps almost no state locally. The ADK session persists only two values on the events it emits: the `previous_interaction_id` and the sandbox `environment_id`. On each new turn the agent recovers both by scanning prior session events, then reuses them so the conversation and its sandbox continue.

Everything else lives server-side. The Managed Agents API owns the sandbox environment and the full interaction history, and that remote interaction, not the local session, is the source of truth for continuing a conversation. Response text appears in both the local ADK events and the remote interaction history, but ADK stores only the IDs it needs to recover and reuse the remote state; it never re-sends prior turns.

## Limitations

- **Location pinned (Agent Platform only):** For the Agent Platform backend, the Managed Agents API is currently served only from the `global` location. Regional endpoints raise an error.
- **Server-side tools only:** Client-executed tools (Python functions, callables) and MCP tools are not supported and raise a `NotImplementedError`.
- **Streaming only:** The agent uses streaming interactions (`stream=True`). Background-polling execution and strictly non-streaming connections are not yet fully supported.
- **Backend differences:** The Gemini API and Agent Platform backends currently exhibit slightly different behavioral patterns. Test against the specific backend you intend to use.

## Next steps

- **Samples:** [Managed Agent Basic](https://github.com/google/adk-python/tree/main/contributing/samples/managed_agent/basic) and [Managed Agent Code Execution](https://github.com/google/adk-python/tree/main/contributing/samples/managed_agent/code_execution).
- **Backend documentation:** [Gemini API Agents](https://ai.google.dev/gemini-api/docs/agents) and [Agent Platform Managed Agents](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/managed-agents).
- **Related ADK topics:** [Models for agents](/agents/models/), [Multi-agent workflows](/workflows/), and [Custom tools](/tools-custom/).
