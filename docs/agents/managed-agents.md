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
