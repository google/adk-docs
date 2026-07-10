# Managed agents

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

Managed agents let you use Google's first-party, out-of-the-box agents—backed by
the Managed Agents API (`interactions.create`)—from within your ADK flows. The
`ManagedAgent` class connects to a managed agent (such as the Antigravity agent)
that runs in a specialized, server-side execution environment, so you get
powerful built-in capabilities without managing sandboxes or writing client-side
function declarations.

`ManagedAgent` implements the same `BaseAgent` contract as other ADK agents, so
you can use it standalone or drop it directly into an ADK flow. It is a good fit
when you want a robust, server-hosted agent with specialized built-in tools
rather than building and operating that environment yourself.

## What are managed agents?

A *managed agent* is an agent whose reasoning, tools, and execution environment
are hosted and operated by Google through the Managed Agents API, rather than run
by your own ADK process. Instead of issuing standard `generate_content` calls,
`ManagedAgent` creates server-side *interactions* and streams the results back
into your ADK flow.

This gives you:

*   **First-party, out-of-the-box agents.** Connect to ready-made agents (for
    example, the Antigravity agent) by referencing their `agent_id`.
*   **Built-in, server-side execution.** Capabilities such as web search and code
    execution run in a managed sandbox on the server—no local sandbox to
    provision or secure.
*   **No client-side function declarations.** Server-side tools are configured on
    the managed agent, so you don't declare or execute them locally.

## Backends and setup

`ManagedAgent` supports two backends. Complete the prerequisites for the backend
you plan to use: obtain credentials and an `agent_id`.

### Gemini API backend

*   **Authentication.** Obtain a Gemini API key and set it as the
    `GEMINI_API_KEY` environment variable.
*   **Agent ID.** You need an `agent_id` to connect to. You can either:
    *   Create a new agent by following the
        [Gemini API Agents documentation](https://ai.google.dev/gemini-api/docs/agents).
    *   Use an out-of-the-box agent ID, such as `antigravity-preview-05-2026`,
        which is used in the examples below.

### Gemini Enterprise Agents Platform (GEAP) backend

The Gemini Enterprise Agents Platform (GEAP) was formerly known as Vertex.

*   **Authentication.** GEAP requires Google Cloud credentials. Follow the
    [GEAP setup instructions](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/managed-agents/create-manage#before-you-begin)
    to authenticate your local environment—for example, with
    `gcloud auth application-default login`.
*   **Location.** The Managed Agents API is served only from the `global`
    location. `ManagedAgent` enforces a connection to `global` on the GEAP
    backend.
*   **Agent ID.** As with the Gemini API, you need an `agent_id`. Create one via
    the [GEAP Managed Agents guide](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/managed-agents),
    or use an out-of-the-box agent ID available to your project.

## Get started

The following example creates two managed agents: one that answers questions
using web search, and one that solves computational questions by running code
server-side. Both run their tools in the managed environment
(`environment={'type': 'remote'}`).

=== "Python"

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

## When to use managed agents vs. building your own

Managed agents and ADK agents solve different problems. Choosing between them is
mostly a trade-off between out-of-the-box power and fine-grained control.

*   **Managed agents** give you a powerful agent out of the box, but with limited
    flexibility. The toolset is predefined and server-side, the agent runs only
    in the managed environment, and client-side or MCP tools are not supported.
*   **ADK agents** (such as [`LlmAgent`](/agents/llm-agents/)) give you
    fine-grained control over the model, instructions, tools (including custom
    function tools and MCP tools), and where execution happens.

Use the following table as a starting point:

| Scenario | Recommended path |
| --- | --- |
| You need web-grounded answers or server-side code execution with no tool or sandbox setup | Managed agent |
| You want to use a first-party, out-of-the-box agent (such as Antigravity) as-is | Managed agent |
| You need custom Python function tools, callables, or MCP tools | Build your own ADK agent |
| You need custom instructions, a specific model, or client-side tool execution | Build your own ADK agent |
| You need a regional (non-`global`) deployment on GEAP | Build your own ADK agent |
