# Quickstart: Consuming a remote agent via A2A

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-typescript">TypeScript v2.5.0</span>
</div>

This quickstart shows you how to consume a remote agent from an Agent Development Kit (ADK) TypeScript agent using the [Agent2Agent (A2A) protocol](https://a2a-protocol.org/). You use `RemoteA2AAgent` to treat a remote A2A service as a standard sub-agent inside your local ADK agent tree.

## Overview

This example builds a multi-agent system that rolls dice locally and checks prime numbers by calling a remote A2A agent:

```text
┌─────────────────┐    ┌──────────────────┐    ┌────────────────────┐
│   Root Agent    │───▶│   Roll Agent     │    │   Remote Prime     │
│   (Local)       │    │   (Local)        │    │   Agent            │
│                 │    │                  │    │  (localhost:8001)  │
│                 │───▶│                  │◀───│                    │
└─────────────────┘    └──────────────────┘    └────────────────────┘
```

The sample consists of three agents:

- **Root Agent** (`root_agent`): The local orchestrator (`LlmAgent`) that delegates tasks to specialized sub-agents.
- **Roll Agent** (`roll_agent`): A local sub-agent that rolls dice using a function tool.
- **Prime Agent** (`prime_agent`): A `RemoteA2AAgent` that delegates prime number checks to a separate A2A server running on port `8001`.

## Set up the project

A2A client support is built into `@google/adk`, so you do not need to install a separate A2A package. If you have not set up an ADK TypeScript environment yet, follow the [TypeScript Quickstart for ADK](../get-started/typescript.md) to install Node.js, initialize your project, and configure `GEMINI_API_KEY` in a `.env` file.

Clone the repository and navigate to the [`a2a_basic` sample](https://github.com/google/adk-docs/tree/main/examples/typescript/snippets/a2a/a2a_basic), then install dependencies:

```bash
cd examples/typescript/snippets/a2a/a2a_basic
npm install
```

The sample directory contains the following files:

```text
a2a_basic/
├── remote_a2a/
│   └── check_prime_agent.ts   # remote agent exposed over A2A
├── agent.ts                   # local root agent consuming the remote agent
├── callbacks.ts               # request callback and metadata example
├── package.json
└── tsconfig.json
```

## Expose and start the remote agent server

To test consuming a remote agent locally, start a separate A2A server that hosts `check_prime_agent`. Because A2A is a wire protocol, the remote server can run in ADK Python, ADK TypeScript, ADK Go, ADK Java, or any A2A-compatible framework.

The sample defines the remote prime-checking agent in `remote_a2a/check_prime_agent.ts`:

```typescript title="a2a_basic/remote_a2a/check_prime_agent.ts"
--8<-- "examples/typescript/snippets/a2a/a2a_basic/remote_a2a/check_prime_agent.ts"
```

Start the ADK API server with the `--a2a` flag on port `8001` to avoid conflicting with port `8000`, which `adk web` uses by default:

```bash
npx adk api_server --a2a --port 8001 remote_a2a
```

!!! note "Local development only"

    This command starts an unauthenticated local server on `localhost` for testing. Configure authentication before exposing an A2A server beyond your local machine.

### Verify the remote agent card

The A2A protocol requires each remote agent to publish an **agent card** describing its identity, capabilities, and RPC endpoints at `/.well-known/agent-card.json`. When you run `npx adk api_server --a2a`, ADK generates and serves this card automatically at `/a2a/<app_name>/.well-known/agent-card.json`, where `<app_name>` is the agent file or directory name, such as `check_prime_agent`.

Verify that the card is reachable:

```bash
curl http://localhost:8001/a2a/check_prime_agent/.well-known/agent-card.json
```

!!! note "A2A protocol version"

    ADK TypeScript uses `@a2a-js/sdk` 0.3.x, which expects A2A 0.3 agent cards that include top-level `url` and `preferredTransport` fields.

## Connect to the remote agent

Import `RemoteA2AAgent` from `@google/adk/a2a`, or from the top-level `@google/adk` package, and pass the remote agent's `name`, `description`, and `agentCard`:

```typescript title="a2a_basic/agent.ts"
--8<-- "examples/typescript/snippets/a2a/a2a_basic/agent.ts:remote_agent"
```

Pass `primeAgent` into `subAgents` on your local `LlmAgent` just like any local sub-agent:

```typescript title="a2a_basic/agent.ts"
--8<-- "examples/typescript/snippets/a2a/a2a_basic/agent.ts:root_agent"
```

The `agentCard` property accepts three forms:

- **HTTP or HTTPS URL:** Resolves the agent card lazily on first invocation using `RemoteA2AAgent`. By default, fetched cards must serve RPC endpoints over HTTPS, or HTTP on loopback hosts such as `localhost`, and share the same origin as the card URL. You can relax these checks for trusted internal deployments with `resolveAgentCardOptions`.
- **Local file path or `file://` URL:** Reads the agent card JSON from disk.
- **Pre-loaded `AgentCard` object:** Uses an in-memory card object directly without making a network fetch.

If you manage your own A2A client lifecycle or connection pool, you can pass a pre-initialized `client` instead of `agentCard`.

## Run the consuming agent

In a separate terminal from the `a2a_basic/` directory, start the ADK web interface:

```bash
npx adk web
```

Open `http://localhost:8000` in your browser, select `agent` from the agent selector, and try these prompts:

**Local dice rolling using `roll_agent`:**

```text
User: Roll a 6-sided die
Agent: I rolled a 6-sided die and got 4.
```

**Remote prime checking delegated to `prime_agent` over A2A:**

```text
User: Is 7 a prime number?
Agent: Yes, 7 is a prime number.
```

**Combined workflow using local `roll_agent` followed by remote `prime_agent`:**

```text
User: Roll a 10-sided die and check if the result is prime.
Agent: I rolled a 7, and 7 is a prime number.
```

## Advanced configuration: callbacks and metadata

You can inspect or modify outgoing A2A requests and incoming A2A stream events using `beforeRequestCallbacks` and `afterRequestCallbacks`, and attach request-level metadata with `metadata`:

```typescript title="a2a_basic/callbacks.ts"
--8<-- "examples/typescript/snippets/a2a/a2a_basic/callbacks.ts:callbacks"
```

- **`beforeRequestCallbacks`**: Runs before sending each request to the remote agent. Mutate `params` in place to adjust metadata or message configuration, or return a rejected `Promise` to abort the request.
- **`afterRequestCallbacks`**: Runs after each A2A response event arrives and before ADK converts it to an ADK `Event`. Return a rejected `Promise` to stop further processing.

For all configuration options—including custom `client` and `clientFactory` overrides, `messageSendConfig`, and `resolveAgentCardOptions`—see the [`RemoteA2AAgentConfig` API reference](../api-reference/typescript/interfaces/RemoteA2AAgentConfig.html).

## Next steps

- [**Introduction to A2A**](./intro.md): Learn how A2A agent cards, tasks, and message exchange work in ADK.
- [**A2A protocol overview**](./index.md): Explore exposing and consuming quickstarts across all supported ADK languages.
- [**TypeScript Quickstart for ADK**](../get-started/typescript.md): Review project setup, CLI commands, and local debugging for ADK TypeScript.
