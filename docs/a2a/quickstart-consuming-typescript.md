# Quickstart: Consuming a remote agent via A2A

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-typescript">TypeScript v2.2.0</span>
</div>

This quickstart shows you how to consume a remote agent from an ADK TypeScript agent using the [Agent2Agent (A2A) Protocol](https://a2a-protocol.org/). You use `RemoteA2AAgent` to treat a remote A2A service as a standard sub-agent inside your local ADK agent tree.

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

Before you start, make sure you have the following installed:

- Node.js 24.13.0 or later
- npm 11.8.0 or later

A2A client support is built into `@google/adk` (you do not need to install a separate A2A package). Create a project directory and install the ADK libraries:

```bash
mkdir -p a2a_basic/remote_a2a
cd a2a_basic
npm init --yes
npm pkg set type="module"
npm pkg set main="agent.ts"
npm install @google/adk zod
npm install -D @google/adk-devtools
```

Set your Gemini API key in a `.env` file in the `a2a_basic/` directory:

```bash
echo 'GEMINI_API_KEY="YOUR_API_KEY"' > .env
```

The complete sample files live in [`examples/typescript/snippets/a2a/a2a_basic`](https://github.com/google/adk-docs/tree/main/examples/typescript/snippets/a2a/a2a_basic):

```text
a2a_basic/
├── remote_a2a/
│   └── check_prime_agent.ts   # remote agent exposed over A2A
├── agent.ts                   # local root agent consuming the remote agent
├── package.json
└── .env
```

## Expose and start the remote agent server

To test consuming a remote agent locally, start a separate A2A server that hosts `check_prime_agent`. Because A2A is a wire protocol, the remote server can run in any ADK language or any A2A-compatible framework.

Create `remote_a2a/check_prime_agent.ts` with the prime-checking agent:

```typescript title="a2a_basic/remote_a2a/check_prime_agent.ts"
--8<-- "examples/typescript/snippets/a2a/a2a_basic/remote_a2a/check_prime_agent.ts"
```

Start the ADK API server with the `--a2a` flag on port `8001` (using a separate port from `8000`, which `adk web` uses by default):

```bash
npx adk api_server --a2a --port 8001 remote_a2a
```

!!! warning "Local development authentication"

    When you omit `--a2a_auth_token` (and `ADK_A2A_AUTH_TOKEN`), `adk api_server --a2a` serves the A2A endpoints without authentication for local development. Always configure authentication before exposing an A2A server beyond localhost.

### Verify the remote agent card

The A2A protocol requires each remote agent to publish an **agent card** describing its identity, capabilities, and RPC endpoints at `/.well-known/agent-card.json`. When you run `npx adk api_server --a2a`, ADK generates and serves this card automatically at `/a2a/<agent_name>/.well-known/agent-card.json`.

Verify that the card is reachable:

```bash
curl http://localhost:8001/a2a/check_prime_agent/.well-known/agent-card.json
```

!!! note "A2A protocol version"

    ADK for TypeScript uses `@a2a-js/sdk` 0.3.x, which expects A2A 0.3 agent cards (with top-level `url` and `preferredTransport` fields).

## Connect to the remote agent

Import `RemoteA2AAgent` from `@google/adk/a2a` (or from the top-level `@google/adk` package) and pass the remote agent's `name`, `description`, and `agentCard`:

```typescript title="a2a_basic/agent.ts"
--8<-- "examples/typescript/snippets/a2a/a2a_basic/agent.ts:remote_agent"
```

Pass `primeAgent` into `subAgents` on your local `LlmAgent` just like any local sub-agent:

```typescript title="a2a_basic/agent.ts"
--8<-- "examples/typescript/snippets/a2a/a2a_basic/agent.ts:root_agent"
```

The `agentCard` property accepts three forms:

- **HTTP or HTTPS URL:** `RemoteA2AAgent` resolves the agent card lazily on first invocation. By default, fetched cards must serve RPC endpoints over HTTPS (or HTTP on loopback hosts such as `localhost`) and share the same origin as the card URL. You can relax these checks for trusted internal deployments with `resolveAgentCardOptions`.
- **Local file path or `file://` URL:** Reads the agent card JSON from disk.
- **Pre-loaded `AgentCard` object:** Uses an in-memory card object directly without making a network fetch.

If you manage your own A2A client lifecycle or connection pool, you can pass a pre-initialized `client` instead of `agentCard`.

## Run the consuming agent

In a separate terminal from the `a2a_basic/` directory, start the ADK web interface:

```bash
npx adk web
```

Open `http://localhost:8000` in your browser, select `agent` (or `root_agent`), and try these prompts:

**Local dice rolling (uses `roll_agent`):**

```text
User: Roll a 6-sided die
Agent: I rolled a 6-sided die and got 4.
```

**Remote prime checking (delegates to `prime_agent` over A2A):**

```text
User: Is 7 a prime number?
Agent: Yes, 7 is a prime number.
```

**Combined workflow (local `roll_agent` followed by remote `prime_agent`):**

```text
User: Roll a 10-sided die and check if the result is prime.
Agent: I rolled a 7, and 7 is a prime number.
```

## Advanced configuration: callbacks and metadata

You can inspect or modify outgoing A2A requests and incoming A2A stream events using `beforeRequestCallbacks` and `afterRequestCallbacks`, and attach request-level metadata with `metadata`:

```typescript title="a2a_basic/callbacks.ts"
--8<-- "examples/typescript/snippets/a2a/a2a_basic/callbacks.ts:callbacks"
```

- **`beforeRequestCallbacks`**: Runs before each request is sent to the remote agent. Mutate `params` in place to adjust metadata or message configuration, or return a rejected `Promise` to abort the request.
- **`afterRequestCallbacks`**: Runs after each A2A response event arrives and before ADK converts it to an ADK `Event`. Return a rejected `Promise` to stop further processing.

### Configuration options (`RemoteA2AAgentConfig`)

In addition to standard `BaseAgentConfig` fields (`name`, `description`, `subAgents`, `beforeAgentCallback`, `afterAgentCallback`), `RemoteA2AAgent` accepts the following options:

| Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `agentCard` | `AgentCard \| string` | `undefined` | Pre-loaded `AgentCard` object, HTTP(S) URL, `file://` URL, or local filesystem path. Either `agentCard` or `client` is required. |
| `resolveAgentCardOptions` | `ResolveAgentCardOptions` | `{ allowInsecureRpc: false, allowCrossOriginRpc: false }` | Controls validation of RPC URLs declared inside a fetched card. |
| `client` | `Client` | `undefined` | Pre-initialized `@a2a-js/sdk` `Client` instance for custom transport or connection pooling. |
| `clientFactory` | `ClientFactory` | Default trace-propagating factory | Custom factory used to construct the A2A `Client` from the resolved `AgentCard`. |
| `messageSendConfig` | `MessageSendConfiguration` | `undefined` | Default A2A message send configuration (such as accepted output modes or blocking behavior). |
| `beforeRequestCallbacks` | `BeforeA2ARequestCallback[]` | `undefined` | Callbacks invoked before sending each A2A request. |
| `afterRequestCallbacks` | `AfterA2ARequestCallback[]` | `undefined` | Callbacks invoked after receiving each raw A2A stream event. |
| `metadata` | `Record<string, unknown>` | `context.a2aMetadata` | Request-level metadata attached to outgoing A2A requests. |

## Next steps

- [**Introduction to A2A**](./intro.md): Learn how A2A agent cards, tasks, and message exchange work in ADK.
- [**A2A Protocol overview**](./index.md): Explore exposing and consuming quickstarts across all supported ADK languages.
- [**TypeScript Quickstart for ADK**](../get-started/typescript.md): Review project setup, CLI commands, and local debugging for ADK TypeScript.
