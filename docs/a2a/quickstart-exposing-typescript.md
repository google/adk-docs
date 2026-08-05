# Quickstart: Exposing a remote agent via A2A

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-typescript">TypeScript</span><span class="lst-preview">Experimental</span>
</div>

This quickstart covers the most common starting point for any developer: **"I have an agent. How do I expose it so that other agents can use my agent via A2A?"**. This is crucial for building complex multi-agent systems where different agents need to collaborate and interact.

## What you'll build

You'll take an ADK agent that rolls dice, wrap it with `toA2a()`, and serve it on
`http://localhost:8001`. By the end you'll have proved it works twice with `curl`: once by
fetching the agent card that A2A clients use to discover your agent, and once by sending it a
real request over JSON-RPC and getting a dice roll back.

```text
┌─────────────────────┐                             ┌───────────────────────────────┐
│  Any A2A client     │       A2A Protocol          │  A2A-Exposed Dice Agent       │
│  (curl, another     │────────────────────────────▶│  toA2a(diceAgent)             │
│   ADK agent, ...)   │                             │  (localhost:8001)             │
└─────────────────────┘                             └───────────────────────────────┘
```

Here is the whole server. The rest of this page walks through it, but this file is complete —
paste it into `server.ts`, add an API key, and it runs:

```typescript title="my-a2a-agent/server.ts"
--8<-- "examples/typescript/a2a_basic/remote_a2a/dice_agent/server.ts:full"
```

## Prerequisites

*   **Node.js 22 or later.** `@google/adk` declares no `engines` field, so npm will not warn
    you if your Node is too old. The example above uses top-level `await` and
    `node --env-file`, both of which need Node 22+.
*   **A Gemini API key.** Create one in Google AI Studio on the
    [API Keys](https://aistudio.google.com/app/apikey) page.
*   **A `.env` file** in your project root containing exactly this line, with your own key
    substituted for `YOUR_API_KEY`:

    ```bash title="my-a2a-agent/.env"
    GEMINI_API_KEY="YOUR_API_KEY"
    ```

    ADK reads `GOOGLE_GENAI_API_KEY` first and falls back to `GEMINI_API_KEY`. Either name
    works; `GOOGLE_API_KEY` alone does not.

!!! note "There is no separate A2A package to install"

    Express and `@a2a-js/sdk` — the HTTP server and the A2A protocol implementation — are
    direct dependencies of `@google/adk`, not peer dependencies. Installing `@google/adk`
    installs everything the A2A server needs. There is also no `@google/adk/a2a` subpath:
    `toA2a` and every other A2A symbol are exported from the package root.

## Expose your agent

### 1. Create the project

```bash
mkdir my-a2a-agent && cd my-a2a-agent
npm init --yes
npm pkg set type="module"
```

`type: "module"` is required. The server uses top-level `await`, which only works in an ES
module.

### 2. Install the dependencies

=== "npm"

    ```bash
    npm install @google/adk zod
    npm install -D tsx typescript @types/node @types/express
    ```

=== "pnpm"

    ```bash
    pnpm add @google/adk zod
    pnpm add -D tsx typescript @types/node @types/express
    ```

=== "yarn"

    ```bash
    yarn add @google/adk zod
    yarn add -D tsx typescript @types/node @types/express
    ```

`zod` defines the tool's parameter schema. Install **zod 4** — `@google/adk` depends on
`zod@^4.2.1`, and a zod 3 install will not typecheck. `tsx` runs TypeScript directly so you
don't need a build step. `@types/express` is only needed if you annotate the request object
when you [add authentication](#turn-on-authentication-before-you-ship); Express itself is
already installed as a dependency of `@google/adk`.

### 3. Add a `tsconfig.json`

```json title="my-a2a-agent/tsconfig.json"
{
  "compilerOptions": {
    "target": "es2022",
    "module": "nodenext",
    "moduleResolution": "nodenext",
    "strict": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "types": ["node"]
  }
}
```

`module: "nodenext"` is the setting that matters: with `commonjs` the top-level `await` in
`server.ts` fails to compile.

### 4. Write the agent and expose it

Create `server.ts` with the code from the top of this page.

```typescript title="my-a2a-agent/server.ts"
--8<-- "examples/typescript/a2a_basic/remote_a2a/dice_agent/server.ts:full"
```

Here's what is happening in this code:

1.  **`rollDice`** is an ordinary ADK `FunctionTool`. The `parameters` schema —
    `z.object({ sides: z.number() })` — is what types the `{ sides }` argument destructured
    inside `execute`, and it is also what A2A clients see as a declared skill.
2.  **`diceAgent`** is an ordinary `LlmAgent`. Nothing about it is A2A-specific; any
    `BaseAgent` can be exposed this way.
3.  **`toA2a(diceAgent, {...})`** returns a `Promise<express.Application>`. It builds the agent
    card, mounts the A2A routes, and hands the app back to you.
4.  **`port: PORT`** writes `http://localhost:8001/jsonrpc` into the agent card. It does *not*
    open a socket. It must agree with the port you pass to `app.listen()` below, or clients
    will read the card successfully and then fail to reach the address it advertises.
5.  **`allowUnauthenticated: true`** is a local-development shortcut: without it, or without an
    `authentication` callback, `toA2a` refuses to start at all. See
    [Turn on authentication before you ship](#turn-on-authentication-before-you-ship) before you expose this on any
    network someone else can reach.
6.  **`app.listen(PORT)`** is yours to call. `toA2a` never listens for you — the application it
    returns is inert until you start it. This is deliberate: it means you can mount the A2A
    routes onto an Express app you already have by passing it as the `app` option.

### 5. Start the server

```bash
npx tsx --env-file=.env server.ts
```

`--env-file=.env` is what loads your API key. ADK does not read `.env` for you when you run a
script directly, so without this flag the agent starts fine and then fails on the first model
call.

You should see:

```console
WARN: [ADK] SECURITY WARNING: Mounting the A2A server WITHOUT authentication because
`allowUnauthenticated: true` was set. The agent and all of its tools are exposed to any
network-reachable caller, which can invoke them with arbitrary input and read the output.
Do NOT use this outside of local, trusted development.
[dice_agent] A2A server listening on http://localhost:8001
[dice_agent] agent card: http://localhost:8001/.well-known/agent-card.json
```

The warning is expected — it is `allowUnauthenticated: true` telling you what it did.

### 6. Fetch the agent card

The agent card is how other agents discover yours: its name, its skills, and the URL to call.
ADK generates it from your agent code; you don't write it by hand. Leave the server running and,
in a second terminal:

```bash
curl -s http://localhost:8001/.well-known/agent-card.json | python3 -m json.tool
```

You should see exactly this (the endpoint is served at the `AGENT_CARD_PATH` constant,
`.well-known/agent-card.json`):

```json
{
    "name": "dice_agent",
    "description": "An agent that rolls dice on request.",
    "protocolVersion": "0.3.0",
    "version": "1.0.0",
    "skills": [
        {
            "id": "dice_agent",
            "name": "model",
            "description": "An agent that rolls dice on request. I roll dice for the user. Always use the roll_dice tool. Report the resulting number in one short sentence.",
            "tags": [
                "llm"
            ]
        },
        {
            "id": "dice_agent-roll_dice",
            "name": "roll_dice",
            "description": "Rolls an N-sided die and returns the result.",
            "tags": [
                "llm",
                "tools"
            ]
        }
    ],
    "url": "http://localhost:8001/jsonrpc",
    "preferredTransport": "JSONRPC",
    "capabilities": {
        "extensions": [],
        "stateTransitionHistory": false,
        "pushNotifications": false,
        "streaming": true
    },
    "defaultInputModes": [
        "text"
    ],
    "defaultOutputModes": [
        "text"
    ],
    "additionalInterfaces": [
        {
            "url": "http://localhost:8001/jsonrpc",
            "transport": "JSONRPC"
        },
        {
            "url": "http://localhost:8001/rest",
            "transport": "HTTP+JSON"
        }
    ]
}
```

Three things in that card are worth noticing:

*   **One skill per capability.** `dice_agent` (the model itself) and `dice_agent-roll_dice`
    (the tool) are advertised separately, so a calling agent can tell what yours can do.
*   **Your instruction came back in the first person.** You wrote *"You roll dice for the
    user"*; the card says *"I roll dice for the user"*. ADK rewrites the pronouns when it
    publishes your instruction as a description. This is intentional — the card speaks as the
    agent.
*   **`url` is `http://localhost:8001/jsonrpc`,** built from the `port` you passed to `toA2a`.
    If that URL doesn't match where you're actually listening, this is where you'll spot it.

### 7. Send it a real request

Now call the agent over the wire, the same way another agent would:

```bash
curl -s -X POST http://localhost:8001/jsonrpc \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "message/send",
    "params": {
      "message": {
        "kind": "message",
        "messageId": "msg-1",
        "role": "user",
        "parts": [{"kind": "text", "text": "Roll a 20-sided die."}]
      }
    }
  }' | python3 -m json.tool
```

The response is an A2A **task**. Its `artifacts` array carries the tool call, the tool result,
and the agent's final answer:

```json
{
    "jsonrpc": "2.0",
    "id": "1",
    "result": {
        "kind": "task",
        "id": "56c9f559-f06b-4340-9eae-305fa2915bc4",
        "contextId": "e5d5ebaa-64a6-4e4a-b349-d2b278711784",
        "history": [
            {
                "kind": "message",
                "messageId": "msg-1",
                "role": "user",
                "parts": [
                    {
                        "kind": "text",
                        "text": "Roll a 20-sided die."
                    }
                ],
                "contextId": "e5d5ebaa-64a6-4e4a-b349-d2b278711784",
                "taskId": "56c9f559-f06b-4340-9eae-305fa2915bc4"
            }
        ],
        "status": {
            "state": "completed",
            "timestamp": "2026-08-05T17:22:09.580Z"
        },
        "artifacts": [
            {
                "artifactId": "f891684f-f842-412a-b8bb-5916e5297b6b",
                "parts": [
                    {
                        "kind": "data",
                        "data": {
                            "name": "roll_dice",
                            "args": {
                                "sides": 20
                            },
                            "id": "adk-cd79ede2-5c93-4e85-9fb8-9adbbbfd80b0"
                        },
                        "metadata": {
                            "adk_type": "function_call"
                        }
                    }
                ]
            },
            {
                "artifactId": "90b1d991-692b-45b2-9fb9-48c975210147",
                "parts": [
                    {
                        "kind": "data",
                        "data": {
                            "id": "adk-cd79ede2-5c93-4e85-9fb8-9adbbbfd80b0",
                            "name": "roll_dice",
                            "response": {
                                "result": 17
                            }
                        },
                        "metadata": {
                            "adk_type": "function_response"
                        }
                    }
                ]
            },
            {
                "artifactId": "a4ed76ad-ca58-47cd-8e0b-28da13070459",
                "parts": [
                    {
                        "kind": "text",
                        "text": "You rolled a 17."
                    }
                ]
            }
        ]
    }
}
```

`"state": "completed"` and `"You rolled a 17."` mean the whole path worked: the request arrived,
the agent ran, the tool fired, and the model's answer came back over A2A. Your server terminal
shows the matching tool call:

```console
[dice_agent] roll_dice(sides=20) -> 17
```

Your agent is now callable by any A2A client. Roll again and you'll get a different number.

## What `toA2a` mounted

`toA2a` installs three routes on the Express app it returns:

| Route | Purpose | Authenticated? |
|---|---|---|
| `/.well-known/agent-card.json` | Agent discovery | **No — always public** |
| `/jsonrpc` | JSON-RPC transport (the card's `preferredTransport`) | Yes, once you configure it |
| `/rest` | HTTP+JSON transport | Yes, once you configure it |

!!! warning "The `basePath` option's documented default is wrong"

    The JSDoc on `ToA2aOptions.basePath` says the default is `"a2a"`. The implementation is
    `options.basePath || ''`, so the real default is an empty string and the routes above sit
    at the root — which is what the card you just fetched shows. If you *do* set
    `basePath: '/a2a'`, the routes move to `/a2a/.well-known/agent-card.json` and clients must
    use a base URL with a **trailing slash** (`http://localhost:8001/a2a/`); without the slash
    `new URL()` drops the segment and the card fetch 404s.

## Turn on authentication before you ship

`allowUnauthenticated: true` is a quickstart shortcut and nothing more: it exposes your agent
and every one of its tools to any caller who can reach the port. For anything beyond a local
loop, replace it with an `authentication` callback — a `UserBuilder` that receives the Express
request, validates its credentials, and returns the authenticated user. Throw to reject.

```typescript title="my-a2a-agent/server.ts"
--8<-- "examples/typescript/a2a_basic/remote_a2a/dice_agent/server-with-auth.ts:auth"
```

The `req: Request` annotation is why `@types/express` is in the dev dependencies — Express
ships with `@google/adk` but its type definitions do not.

With that in place:

```console
$ curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:8001/.well-known/agent-card.json
HTTP 200

$ curl -s -X POST http://localhost:8001/jsonrpc -H 'Content-Type: application/json' -d '...'
{"jsonrpc":"2.0","id":"1","error":{"code":-32603,"message":"General processing error."}}

$ curl -s -X POST http://localhost:8001/jsonrpc -H 'Authorization: Bearer s3cret-token' -d '...'
{"jsonrpc":"2.0","id":"1","result":{"kind":"task", ... "state":"completed" ... }}
```

Two things to plan for:

*   **The agent card stays public.** `authentication` gates `/jsonrpc` and `/rest` only.
    Discovery is meant to be open, so do not put anything secret in your agent's name,
    description, or instruction.
*   **A rejected request is an HTTP 500, not a 401.** The body is JSON-RPC error code
    `-32603`, `"General processing error."`, with no hint that credentials were the problem.

## Should you use `toA2a`?

Use `toA2a` when you want *another agent* to call yours over the network, and you want to own
the HTTP server — you get an Express app, so you choose the port, the middleware, the TLS
termination, and the process manager.

*   If you want a **local dev loop with a chat UI** rather than a network endpoint, run
    `adk web` from `@google/adk-devtools` instead; see the
    [TypeScript quickstart](../get-started/typescript.md).
*   If you want your agent to **call** a remote A2A agent rather than be called, you want
    [A2A Quickstart (Consuming)](./quickstart-consuming-typescript.md) — `RemoteA2AAgent`, not
    `toA2a`.
*   If the two agents are in the **same process**, you don't need A2A at all. Compose them
    directly with [sub-agents and workflow agents](../workflows/index.md).

## Troubleshooting

??? failure "`fetch failed`, with no other detail"

    The port in the agent card doesn't match the port you're actually listening on. `toA2a`'s
    `port` option only writes the URL into the card; `app.listen()` is what opens the socket.
    When they disagree the client fetches the card successfully, POSTs to the dead address it
    advertises, and reports:

    ```console
    ERROR: [ADK] A2ARemoteAgent remote_echo failed: TypeError: fetch failed
    ```

    Confirm with `curl -s http://localhost:8001/.well-known/agent-card.json | grep '"url"'` —
    if the URL names a port nothing is bound to, that's the bug. Use one `PORT` constant for
    both.

??? failure "`toA2a: refusing to mount the A2A server without authentication`"

    You called `toA2a(agent)` without `allowUnauthenticated` and without `authentication`.
    `toA2a` fails closed, and the rejected promise reads:

    ```console
    toA2a: refusing to mount the A2A server without authentication. The A2A surface lets any
    network-reachable caller invoke this agent and its tools with arbitrary input and read the
    output, so it must be authenticated. Provide `authentication` (a UserBuilder that validates
    the request, e.g. a bearer token or OIDC credential) or, only for local/trusted development,
    explicitly set `allowUnauthenticated: true`.
    ```

    Pass `allowUnauthenticated: true` locally, or an `authentication` callback anywhere else.

??? failure "HTTP 500 and `-32603` on every request once auth is on"

    ```console
    {"jsonrpc":"2.0","id":"1","error":{"code":-32603,"message":"General processing error."}}
    ```

    This *is* the authentication failure. A rejected `UserBuilder` surfaces as a generic
    JSON-RPC internal error, not a 401 or 403, and the message says nothing about credentials —
    so don't go looking for a 401 in your logs. Check that the caller is sending the header your
    `authentication` callback reads, then log inside the callback to see the value it received.

??? failure "`Failed to fetch Agent Card from .../.well-known/.well-known/agent-card.json: 404`"

    A client was given the card URL where it expects the **base URL**. The A2A resolver appends
    `.well-known/agent-card.json` itself, so passing the full card URL doubles the path:

    ```console
    UNCAUGHT: Failed to fetch Agent Card from
    http://localhost:8001/.well-known/.well-known/agent-card.json: 404
    ```

    Note that this one is an uncaught exception that stops the client process, not a tidy error
    event. Pass `http://localhost:8001`, not
    `http://localhost:8001/.well-known/agent-card.json`.

??? failure "`Type 'ZodObject<...>' is not assignable to type 'ToolInputParameters'`"

    You have zod 3 installed and `@google/adk` needs zod 4:

    ```console
    error TS2322: Type 'ZodObject<{ sides: ZodNumber; }, "strip", ZodTypeAny, { sides: number; },
    { sides: number; }>' is not assignable to type 'ToolInputParameters'.
    ```

    Run `npm install zod@^4.2.1`. The server may still run — the mismatch is only visible to
    `tsc` — but the types are lying to you until you fix it.

??? failure "`API key not valid. Please pass a valid API key.` in the task response"

    The A2A layer is fine; the model call is not. This error arrives as a `"state": "failed"`
    task, which means the request reached your agent and the failure travelled back correctly.
    Either the key in `.env` is wrong, or you started the server without `--env-file=.env` and
    ADK never saw it.

## Next steps

*   **[Call this agent from another ADK agent](./quickstart-consuming-typescript.md)** — wire it
    up as a `RemoteA2AAgent` so a parent agent can delegate to it.
*   **[Give the exposed agent more tools](../tools-custom/function-tools.md)** — every tool you
    add shows up as a new skill in the agent card automatically.
*   **[Understand how A2A fits into multi-agent systems](./intro.md)** — when to reach for a
    remote agent instead of a sub-agent.
*   **[Browse the complete runnable example](https://github.com/google/adk-docs/tree/main/examples/typescript/a2a_basic)**
    — the `server.ts` and authenticated variant from this page, ready to `npm install && npm run serve`.
