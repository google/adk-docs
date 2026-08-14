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
│   (Local)       │◀────────│   (localhost:9090)     │
└─────────────────┘         └────────────────────────┘
```

- **Root Agent** (`root_agent`): The local orchestrator that delegates to sub-agents
- **Prime Agent** (`prime_agent`): A remote A2A agent that checks whether a number is prime, running on a separate A2A server

## Add the A2A dependency

A2A support ships in a separate artifact. The A2A SDK client is needed on the
compile classpath as well, because `A2AAgent`'s `httpClient` parameter defaults
to `JdkA2AHttpClient()`:

```kotlin title="build.gradle.kts"
implementation("com.google.adk:google-adk-kotlin-a2a:0.7.0")
implementation("org.a2aproject.sdk:a2a-java-sdk-client:1.0.0.Final")
```

## Start a remote agent server

To consume a remote agent you first need one running. adk-kotlin cannot expose an
agent over A2A yet, so the server has to come from elsewhere — A2A is a wire
protocol, so any language will do.

The A2A protocol requires each agent to publish an **agent card** describing what
it does, served at the well-known path:

```text
http://localhost:9090/.well-known/agent-card.json
```

The Kotlin client reads **A2A 1.0** cards, so the card must carry a
`supportedInterfaces` array whose entries each have a `protocolBinding`.
Cards written for A2A 0.3 omit it, and `A2AAgent` rejects them with
`AgentCardResolutionError: Failed to parse agent card`. That includes the
`a2a_server` sample in adk-java and the `remote_a2a` sample in adk-python as
they stand today, so neither works as the server for this page yet.

A minimal card the client accepts looks like this:

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

Check the card is reachable before you continue:

```bash
curl http://localhost:9090/.well-known/agent-card.json
```

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
