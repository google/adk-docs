# Quickstart: Consuming a remote agent via A2A

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-kotlin">Kotlin</span><span class="lst-preview">Experimental</span>
</div>

This quickstart covers the most common starting point for any developer: **"There is a remote agent, how do I let my ADK agent use it via A2A?"**. This is crucial for building complex multi-agent systems where different agents need to collaborate and interact.

## Overview

This sample demonstrates the **Agent2Agent (A2A)** architecture in the Agent Development Kit (ADK) for Kotlin, showing how a local agent delegates part of a task to an agent running elsewhere.

```text
┌─────────────────┐         ┌────────────────────────┐
│   Root Agent    │────────▶│   Remote Prime Agent   │
│   (Local)       │◀────────│   (localhost:8001)     │
└─────────────────┘         └────────────────────────┘
```

- **Root Agent** (`root_agent`): The local orchestrator that delegates to sub-agents
- **Prime Agent** (`prime_agent`): A remote A2A agent that checks whether a number is prime, running on a separate A2A server

## Add the A2A dependency

A2A support ships in a separate artifact. The A2A SDK client is needed on the
compile classpath as well, because `A2AAgent`'s `httpClient` parameter defaults
to `JdkA2AHttpClient()`:

```kotlin title="build.gradle.kts"
--8<-- "examples/inline/kotlin/a2a/quickstart-consuming-kotlin/001-add-the-a2a-dependency.kt"
```

## Start a remote agent server

To consume a remote agent you first need one running. adk-kotlin cannot expose an
agent over A2A yet, so the server has to come from elsewhere — A2A is a wire
protocol, so any language will do.

The `a2a_basic` sample in adk-python serves the prime agent this page delegates
to. From an adk-python checkout:

```bash
adk api_server --a2a --port 8001 contributing/samples/a2a/a2a_basic/remote_a2a
```

The A2A protocol requires each agent to publish an **agent card** describing what
it does, served at the well-known path under that agent's own prefix:

```text
http://localhost:8001/a2a/check_prime_agent/.well-known/agent-card.json
```

Check the card is reachable before you continue:

```bash
curl http://localhost:8001/a2a/check_prime_agent/.well-known/agent-card.json
```

!!! note "Which servers this client can talk to"

    The Kotlin client reads **A2A 1.0** cards, so the card must carry a
    `supportedInterfaces` array whose entries each have a `protocolBinding`.
    Cards written for A2A 0.3 declare a top-level `url` and `preferredTransport`
    instead, and `A2AAgent` rejects them with
    `AgentCardResolutionError: Failed to parse agent card`.

    The sample's checked-in `agent.json` is a 0.3-style card, but adk-python does
    not serve that file verbatim: it parses the card on startup, and under
    a2a-sdk 1.x that parse promotes `url` and `preferredTransport` into
    `supportedInterfaces`. adk-python requires `a2a-sdk>=0.3.4,<2`, so a fresh
    install resolves to 1.x and the card on the wire is A2A 1.0.

    The `a2a_server` sample in adk-java is pinned to the 0.3.x A2A SDK and serves
    a 0.3 card, so it does not work as the server for this page.

??? note "Serving your own card instead"

    Any server publishing an A2A 1.0 card will do. A minimal card the client
    accepts, served from `<your-base-url>/.well-known/agent-card.json`:

    ```json title=".well-known/agent-card.json"
    {
      "name": "check_prime_agent",
      "description": "Checks whether numbers are prime.",
      "version": "1.0.0",
      "url": "http://localhost:9090",
      "preferredTransport": "JSONRPC",
      "capabilities": { "streaming": true },
      "defaultInputModes": ["text/plain"],
      "defaultOutputModes": ["application/json"],
      "skills": [],
      "supportedInterfaces": [
        { "protocolBinding": "JSONRPC", "url": "http://localhost:9090" }
      ]
    }
    ```

    Pass that base URL — `http://localhost:9090` — as `agentCardUrl` below.

## Connect to the remote agent

`A2AAgent` fetches that card and reads the remote agent's description from it,
along with whether the remote supports streaming. The `name` you pass is this
agent's identifier in your own agent tree, independent of the name the card
advertises. It is a suspending function, so call it from a coroutine:

```kotlin title="A2AConsumer.kt"
--8<-- "examples/kotlin/snippets/a2a/A2AConsumer.kt:remote_agent"
```

If you already hold an `AgentCard` — for example one you resolved yourself, or a
static card checked into your configuration — there is a non-suspending overload
that takes it directly, `A2AAgent(name = ..., agentCard = ...)`.

## Use it as a sub-agent

The returned agent is a `BaseAgent`, so it goes into `subAgents` exactly like a
local one. ADK handles the A2A protocol over the wire:

```kotlin title="A2AConsumer.kt"
--8<-- "examples/kotlin/snippets/a2a/A2AConsumer.kt:root_agent"
```

## Next Steps

Exposing a Kotlin agent over A2A is not yet supported; adk-kotlin currently
provides the consuming side only. To expose an agent, see the quickstarts for
the other languages:

- [**A2A Quickstart (Exposing) for Python**](./quickstart-exposing.md)
- [**A2A Quickstart (Exposing) for Java**](./quickstart-exposing-java.md)
