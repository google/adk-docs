# Expose an ADK agent as an MCP server

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-preview">Experimental</span>
</div>

This quickstart answers a common question: **"I have an agent. How do I expose
it so that any MCP host, such as Claude Code, OpenAI Codex, or an IDE, can drive
it?"** The `to_mcp_server` function turns a whole ADK agent into a standard
[Model Context Protocol](https://modelcontextprotocol.io/) server. It is the MCP
counterpart of [`to_a2a`](/a2a/quickstart-exposing/).

!!! note "Exposing an agent vs. exposing tools"
    This page is about exposing an entire **agent** as a single MCP tool. If you
    instead want to expose individual ADK **tools** to MCP clients, see
    [MCP Tools](/tools-custom/mcp-tools/).

## Overview

`to_mcp_server` registers the agent, its model loop and all of its tools, as a
*single* MCP tool named after the agent. A host that speaks MCP sends a request
string and receives the agent's final response. The host never imports ADK and
never sees the agent's individual tools.

Where `to_a2a` publishes an agent over A2A, `to_mcp_server` publishes it over
MCP, so coding agents and IDEs that already speak MCP can delegate a task to an
ADK agent as if it were any other tool. It builds on `Runner` to execute the
agent and returns a `FastMCP` server, leaving the choice of transport (stdio for
local hosts, streamable-http for networked ones) to the caller.

```text
                        ┌────────────────────┐
                        │      ADK agent     │
                        │  (model + tools)   │
                        └─────────┬──────────┘
                                  │  to_mcp_server(agent)
                                  ▼
                        ┌────────────────────┐
                        │    FastMCP server  │
                        │  one tool = agent  │
                        └─────────┬──────────┘
                                  │  stdio / streamable-http
                                  ▼
                     MCP host (Claude Code, Codex, IDE)
```

## Prerequisites

Install ADK with the `mcp` extra:

```bash
pip install "google-adk[mcp]"
```

## Get started

Define an agent and expose it. Running the file starts the MCP server on stdio,
and an MCP host can launch it as a subprocess.

```python
import random

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import to_mcp_server


def roll_die(sides: int) -> int:
  """Roll a die with the given number of sides and return the result."""
  return random.randint(1, sides)


dice_agent = LlmAgent(
    name="dice_agent",
    description="Rolls dice with any number of sides and reports the outcome.",
    instruction="Use the roll_die tool to roll the dice the user asks for.",
    tools=[roll_die],
)

# The whole agent becomes one MCP tool named "dice_agent".
server = to_mcp_server(dice_agent)

if __name__ == "__main__":
  server.run(transport="stdio")
```

A host configured to launch this file sees one tool, `dice_agent`, and calls it
with a `request` string. The ADK agent runs its own model and `roll_die` loop and
returns the answer.

## How it works

`to_mcp_server` creates a `FastMCP` server and registers one tool whose handler
runs the agent through a `Runner`. If no `runner` is supplied, one is built with
in-memory session, artifact, memory, and credential services.

On each tool call the handler:

1. Resolves an ADK session, then wraps the incoming `request` string as a user
   `Content`.
2. Drives `Runner.run_async` and iterates the event stream.
3. Forwards intermediate (non-final) text events to the host as MCP **progress
   notifications**, so the host can show the agent working in real time.
4. Maps the parts of the final response to MCP content blocks: text becomes
   `TextContent`, inline image data becomes `ImageContent`, audio becomes
   `AudioContent`, and any other inline data becomes an `EmbeddedResource`. A
   multimodal agent's output is preserved rather than flattened to text.

### Session continuity

`to_mcp_server` keeps one ADK session per MCP connection, so successive tool
calls on the same connection form a single multi-turn conversation. Over stdio
there is one connection per process, so all calls share one conversation. Over
streamable-http each client connection gets its own session.

## Configuration options

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `agent` | `BaseAgent` | *required* | The agent to serve. Its model loop and all of its tools are exposed together as one MCP tool. |
| `name` | `str \| None` | `None` | The MCP server and tool name. Defaults to the agent's name (or `"adk_agent"`). Set it when you want the tool to appear under a different name. |
| `instructions` | `str \| None` | `None` | Optional server instructions an MCP host may surface to its model to describe how to use the tool. |
| `runner` | `Runner \| None` | `None` | A pre-built `Runner`. If omitted, one is created with in-memory services. Supply your own to use persistent or custom session, artifact, memory, or credential services. This is the recommended path for a long-lived networked server. |

## Serving over the network

To reach the agent from another machine, run the same server with the networked
transport. Nothing about the agent changes, only the transport differs:

```python
server.run(transport="streamable-http")
```

For a long-lived networked server, inject a `Runner` with a persistent session
service so sessions do not accumulate in memory:

```python
to_mcp_server(agent, runner=my_runner)
```

## Limitations

- **Text input only**: the tool accepts a single `request` string. Passing media
  *into* the agent through the tool call is not supported, because MCP tool
  arguments are JSON that the host's model fills in, and hosts do not place media
  in tool arguments. For media input, use MCP resources or elicitation instead.
- **Default services are in-memory**: for a long-lived streamable-http server,
  sessions accumulate with no eviction. Inject a `runner` with a persistent or
  cleaning session service. Tool calls on a single connection are expected to be
  sequential, since they share one session.
- **Experimental**: `to_mcp_server` is experimental and lives behind the `mcp`
  extra. Its behavior may change in future releases.

## Related

- [Model Context Protocol (MCP) overview](index.md)
- [MCP Tools](/tools-custom/mcp-tools/): expose individual ADK tools instead of a whole agent.
- [Quickstart: Exposing a remote agent via A2A](/a2a/quickstart-exposing/): the A2A counterpart.
