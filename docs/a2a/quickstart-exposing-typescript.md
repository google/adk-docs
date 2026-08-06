# Quickstart: Exposing a remote agent via A2A

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-typescript">TypeScript</span><span class="lst-preview">Experimental</span>
</div>

This quickstart covers the most common starting point for any developer: **"I have an agent. How do I expose it so that other agents can use my agent via A2A?"**. This is crucial for building complex multi-agent systems where different agents need to collaborate and interact.

## Overview

This sample demonstrates how you can easily expose an ADK agent so that it can be then consumed by another agent using the A2A Protocol.

In TypeScript, you expose an agent with the `toA2a()` function, which auto-generates the agent card and returns an Express application that you serve yourself.

```text
┌─────────────────────┐                             ┌───────────────────────────────┐
│  Any A2A client     │       A2A Protocol          │  A2A-Exposed Dice Agent       │
│  (curl, another     │────────────────────────────▶│  toA2a(diceAgent)             │
│   ADK agent)        │                             │      (localhost: 8001)        │
└─────────────────────┘                             └───────────────────────────────┘
```

The sample consists of:

- **Remote Dice Agent** (`remote_a2a/dice_agent/server.ts`): This is the agent that you want to expose so that other agents can use it via A2A. It is an agent that rolls dice. It becomes exposed using the `toA2a()` function and served with `app.listen()`.
- **Authenticated variant** (`remote_a2a/dice_agent/server-with-auth.ts`): The same agent behind a bearer-token check, covered in [Advanced Configuration](#advanced-configuration-authenticating-the-a2a-endpoint).

Reach for `toA2a()` when you want *another agent* to call yours over the network and you want to own the HTTP server — you pick the port, the middleware, and the TLS termination. If the two agents run in the **same process**, you do not need A2A at all: compose them directly with [sub-agents and workflow agents](../workflows/index.md). You need **Node.js 22 or later** — `@google/adk` declares no `engines` field, so nothing warns you on an older runtime, and the sample uses ESM and top-level `await`. The `curl` commands below pipe through [`jq`](https://jqlang.github.io/jq/); if you would rather not install it, drop the `| jq …` and the responses are still valid JSON.

## Exposing the Remote Agent with the `toA2a()` function

You can take an existing agent built using ADK and make it A2A-compatible by wrapping it with `toA2a()`. Nothing about the agent itself has to change — any `BaseAgent` can be exposed this way. `toA2a()` builds the agent card in memory by extracting the name, description, instruction and tools from your ADK agent, so the well-known agent card endpoint is served as soon as you start listening.

!!! note "There is no separate A2A package to install"

    Express and `@a2a-js/sdk` — the HTTP server and the A2A protocol implementation — are direct
    dependencies of `@google/adk`, not peer dependencies, so installing `@google/adk` installs
    everything A2A needs. There is also no `@google/adk/a2a` subpath: every A2A symbol is
    exported from the package root.

### Under the hood: the routes `toA2a()` mounts

`toA2a()` installs three routes on the Express app it returns:

| Route | Purpose | Authenticated? |
|---|---|---|
| `/.well-known/agent-card.json` | Agent discovery | **No — always public** |
| `/jsonrpc` | JSON-RPC transport (the card's `preferredTransport`) | Yes, once you configure it |
| `/rest` | HTTP+JSON transport | Yes, once you configure it |

??? note "Moving the routes with `basePath`"

    By default all three sit at the root. `basePath: '/a2a'` moves them: the card is then at
    `/a2a/.well-known/agent-card.json`, the root card 404s, and the card's `url` becomes
    `http://localhost:8001/a2a/jsonrpc`. Clients must give that base URL a **trailing slash**
    (`http://localhost:8001/a2a/`) — without one, `new URL()` drops the last segment.

### 1. Getting the Sample Code { #getting-the-sample-code }

You can clone and navigate to the [**`a2a_basic`** sample](https://github.com/google/adk-docs/tree/main/examples/typescript/a2a_basic) here:

```bash
git clone https://github.com/google/adk-docs.git
cd adk-docs/examples/typescript/a2a_basic
npm install
```

As you'll see, the folder structure is as follows:

```text
a2a_basic/
├── remote_a2a/
│   └── dice_agent/
│       ├── server.ts            # Remote Dice Agent
│       └── server-with-auth.ts  # The same agent, behind a bearer token
├── package.json
├── tsconfig.json
├── README.md
├── remote_prime_agent.ts        # ─┐
├── direct_client.ts             #  ├─ A2A Quickstart (Consuming) uses these
└── consuming_agent.ts           # ─┘
```

`a2a_basic/` is shared with [A2A Quickstart (Consuming)](./quickstart-consuming-typescript.md). Every server in it listens on port 8001, so run one at a time.

#### Remote Dice Agent (`a2a_basic/remote_a2a/dice_agent/server.ts`)

- **`rollDice`**: A `FunctionTool` whose zod `parameters` type the `{ sides }` argument destructured inside `execute`, and are what A2A clients see as a declared skill.
- **`diceAgent`**: An ordinary `LlmAgent`. Nothing about it is A2A-specific.
- **`toA2a(diceAgent, {...})`**: Returns a `Promise<express.Application>` with the A2A routes mounted. It never listens for you, so **`app.listen(PORT)`** is yours to call — which is also what lets you mount the A2A routes onto an Express app you already have, by passing it as the `app` option.

```typescript title="a2a_basic/remote_a2a/dice_agent/server.ts"
--8<-- "examples/typescript/a2a_basic/remote_a2a/dice_agent/server.ts:full"
```

If you are building this from scratch instead of cloning, run `npm init --yes && npm pkg set type="module"`, then `npm install @google/adk zod` and `npm install -D tsx typescript @types/node @types/express`, and copy the sample's `tsconfig.json`. Two settings are load-bearing: `"type": "module"` in `package.json` and `"module": "nodenext"` in `tsconfig.json`, because the server uses top-level `await`. Keep `zod` on **v4** — `@google/adk` depends on `zod@^4.2.1`, and a zod 3 install makes `tsc` reject every tool schema you write.

!!! warning "`toA2a()` fails closed without authentication"

    `allowUnauthenticated: true` is a local-development shortcut. Without it, and without an
    `authentication` callback, `toA2a()` refuses to mount and the returned promise rejects with
    `toA2a: refusing to mount the A2A server without authentication`. See
    [Advanced Configuration](#advanced-configuration-authenticating-the-a2a-endpoint) before you
    put the agent on a network anyone else can reach.

Finally, create a **`.env` file** next to `package.json` with your model credentials:

=== "Google AI Studio"

    ```bash title="a2a_basic/.env"
    GOOGLE_GENAI_API_KEY="YOUR_API_KEY"
    ```

    Create the key on the [API Keys](https://aistudio.google.com/app/apikey) page. ADK reads
    `GOOGLE_GENAI_API_KEY` first and falls back to `GEMINI_API_KEY`. Either name works;
    `GOOGLE_API_KEY` alone does not.

=== "Google Cloud / Vertex AI"

    ```bash title="a2a_basic/.env"
    GOOGLE_GENAI_USE_VERTEXAI=true
    GOOGLE_CLOUD_PROJECT="your-project-id"
    GOOGLE_CLOUD_LOCATION="global"
    ```

    There is no key on this path: the model call is authenticated with Application Default
    Credentials, so run `gcloud auth application-default login` once and make sure the Vertex AI
    API is enabled on the project. `GOOGLE_GENAI_USE_VERTEXAI=true` is the switch — with it set,
    ADK routes `gemini-2.5-flash` to Vertex AI and ignores `GEMINI_API_KEY` entirely.

### 2. Start the Remote A2A Agent server { #start-the-remote-a2a-agent-server }

You can now start the remote agent server, which will host the A2A app wrapping the dice agent:

```bash
npx tsx --env-file=.env remote_a2a/dice_agent/server.ts    # or: npm run serve:dice
```

Once executed, you should see something like:

```console
WARN: [ADK] 2026-08-06T21:16:38.297Z SECURITY WARNING: Mounting the A2A server WITHOUT authentication because `allowUnauthenticated: true` was set. The agent and all of its tools are exposed to any network-reachable caller, which can invoke them with arbitrary input and read the output. Do NOT use this outside of local, trusted development.
(node:2807369) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
(Use `node --trace-deprecation ...` to show where the warning was created)
[dice_agent] A2A server listening on http://localhost:8001
[dice_agent] agent card: http://localhost:8001/.well-known/agent-card.json
```

All three warning lines are expected: the `SECURITY WARNING` is `allowUnauthenticated: true` telling you what it did, and the `punycode` deprecation is Node 22 complaining about one of ADK's transitive dependencies.

!!! warning "`--env-file=.env` is what loads your credentials"

    ADK does not read `.env` for you when you run a script directly, which is why the command
    above passes Node's `--env-file`. Start the server without it and it comes up perfectly, then
    fails on the first model call — the request reaches your agent and comes back as a
    `"state": "failed"` task carrying `API key not valid. Please pass a valid API key.` (or, on
    the Vertex AI path, a credentials error from `aiplatform.googleapis.com`).

??? note "Why use port 8001?"
    In this quickstart, when testing locally, your agents will be using localhost, so the `port` for the A2A server for the exposed agent must be different from the consuming agent's port. The default port for `adk web` is `8000`, which is why the A2A server is created using a separate port, `8001`.

### 3. Check that your remote agent is running { #check-that-your-remote-agent-is-running }

You can check that your agent is up and running by visiting the agent card that `toA2a()` auto-generated. The card is how other agents discover yours — its name, its skills, and the URL to call — and you never write it by hand:

[http://localhost:8001/.well-known/agent-card.json](http://localhost:8001/.well-known/agent-card.json)

You should see the contents of the agent card. Leave the server running and, in a second terminal, pull out the identity and the skills:

```bash
curl -s http://localhost:8001/.well-known/agent-card.json \
  | jq '{name, description, url, skills: [.skills[] | {id, name, description}]}'
```

```json
{
  "name": "dice_agent",
  "description": "An agent that rolls dice on request.",
  "url": "http://localhost:8001/jsonrpc",
  "skills": [
    {
      "id": "dice_agent",
      "name": "model",
      "description": "An agent that rolls dice on request. I roll dice for the user. Always use the roll_dice tool. Report the resulting number in one short sentence."
    },
    {
      "id": "dice_agent-roll_dice",
      "name": "roll_dice",
      "description": "Rolls an N-sided die and returns the result."
    }
  ]
}
```

Two things in that card are worth noticing. **One skill per capability:** `dice_agent` (the model itself) and `dice_agent-roll_dice` (the tool) are advertised separately, so a calling agent can tell what yours can do. And **your instruction came back in the first person** — you wrote *"You roll dice for the user"*, the card says *"I roll dice for the user"*. ADK rewrites the pronouns when it publishes your instruction as a description; the card speaks as the agent.

The rest of the card, which ADK fills in for you, is the protocol plumbing:

```json
{"protocolVersion":"0.3.0","version":"1.0.0","preferredTransport":"JSONRPC","capabilities":{"extensions":[],"stateTransitionHistory":false,"pushNotifications":false,"streaming":true},"defaultInputModes":["text"],"defaultOutputModes":["text"],"additionalInterfaces":[{"url":"http://localhost:8001/jsonrpc","transport":"JSONRPC"},{"url":"http://localhost:8001/rest","transport":"HTTP+JSON"}]}
```

!!! warning "Check the card's `url` before you blame the client"

    `url` is built from the `port` you passed to `toA2a()`, not from the socket `app.listen()`
    opened. If they disagree, a client reads the card, POSTs to the dead address it advertises,
    and reports nothing more useful than `TypeError: fetch failed`. Use one `PORT` for both.

### 4. Run the Main (Consuming) Agent { #run-the-main-consuming-agent }

Now call the agent over the wire, the same way another agent would. Any A2A client works; `curl` keeps it to one command. The response is an A2A **task**, and the `jq` filter below pulls out the three things that prove it worked — the task's state, the shape of its `artifacts` array, and the agent's final answer:

```bash
curl -s -X POST http://localhost:8001/jsonrpc -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":"1","method":"message/send","params":{"message":{
        "kind":"message","messageId":"msg-1","role":"user",
        "parts":[{"kind":"text","text":"Roll a 20-sided die."}]}}}' \
  | jq -c '.result.status.state,
           [.result.artifacts[].parts[0] | .metadata.adk_type // "text"],
           .result.artifacts[-1].parts[0].text'
```

To do the same thing from an ADK agent instead of `curl` — a `RemoteA2AAgent` that a parent agent can delegate to — follow [A2A Quickstart (Consuming)](./quickstart-consuming-typescript.md).

## Example Interactions

Once the server is running, you can send it requests to see how an A2A client drives your agent.

**Simple Dice Rolling:**

```console
"completed"
["function_call","function_response","text"]
"You rolled a 3."
```

`"completed"` and `"You rolled a 3."` mean the whole path worked: the request arrived, the agent ran, the tool fired, and the model's answer came back over A2A. The middle line is the artifacts array — one artifact for the tool call, one for the tool's result, one for the final text, in that order. Your server terminal shows the matching tool call:

```console
[dice_agent] roll_dice(sides=20) -> 3
```

Roll again and you'll get a different number, and possibly a different sentence around it: the last artifact is the model's own wording, so compare the shape of the response rather than its exact words.

## Advanced Configuration: Authenticating the A2A endpoint

`allowUnauthenticated: true` is a quickstart shortcut and nothing more: it exposes your agent and every one of its tools to any caller who can reach the port. For anything beyond a local loop, replace it with an `authentication` callback — a `UserBuilder` that receives the Express request, validates its credentials, and returns the authenticated user. Throw to reject.

`server-with-auth.ts` is a **complete file**, not a fragment — the same dice agent as before, with `allowUnauthenticated: true` replaced by a bearer-token `authentication` callback:

```typescript title="a2a_basic/remote_a2a/dice_agent/server-with-auth.ts"
--8<-- "examples/typescript/a2a_basic/remote_a2a/dice_agent/server-with-auth.ts:full"
```

Three details in there are worth copying rather than simplifying. **The `req: Request` annotation** is why `@types/express` is a dev dependency — Express ships with `@google/adk` but its type definitions do not. **The token comes from the environment**: add `A2A_SHARED_TOKEN="s3cret-token"` to the same `.env` you already have, rather than prefixing the command with it, because command-line arguments are visible to anyone who can run `ps` and stay in your shell history. And **the comparison is constant-time** — `token === EXPECTED_TOKEN` returns as soon as the two strings diverge, which leaks how much of the secret a caller has guessed; hashing both sides to a fixed-length digest and comparing them with `crypto.timingSafeEqual` does not.

Start it, then reuse the request body from step 4 to see the difference the header makes (Node's `punycode` lines are omitted below):

```console
$ npx tsx --env-file=.env remote_a2a/dice_agent/server-with-auth.ts
[dice_agent] authenticated A2A server on http://localhost:8001

$ BODY='{"jsonrpc":"2.0","id":"1","method":"message/send","params":{"message":{"kind":"message","messageId":"msg-1","role":"user","parts":[{"kind":"text","text":"Roll a 20-sided die."}]}}}'

$ curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:8001/.well-known/agent-card.json
HTTP 200

$ curl -s -w "\nHTTP %{http_code}\n" -X POST http://localhost:8001/jsonrpc \
    -H "Content-Type: application/json" -d "$BODY"
{"jsonrpc":"2.0","id":"1","error":{"code":-32603,"message":"General processing error."}}
HTTP 500

$ curl -s -X POST http://localhost:8001/jsonrpc \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer s3cret-token" -d "$BODY" \
  | jq -c '.result.status.state, .result.artifacts[-1].parts[0].text'
"completed"
"You rolled a 17."
```

A wrong token (`Authorization: Bearer wrong-token`) is byte-for-byte the same rejection as sending no header at all. Two things to plan for:

*   **The agent card stays public.** `authentication` gates `/jsonrpc` and `/rest` only, which
    is why the first `curl` above returns `200`. Discovery is meant to be open, so do not put
    anything secret in your agent's name, description, or instruction.
*   **A rejected request is an HTTP 500, not a 401.** The body is JSON-RPC error code `-32603`,
    `"General processing error."`, with no hint that credentials were the problem — and a
    callback that *crashes* (a typo, a missing import) looks identical to the caller, so check
    that correctly-authenticated callers still get through. The real reason is only on the
    server's own stderr, which prints
    `Unhandled error in JSON-RPC POST handler: Error: A2A request rejected: bad bearer token.`
    and a stack trace.

## Next Steps

Now that you have created an agent that's exposing a remote agent via an A2A server, the next step is to learn how to consume it from another agent.

- [**A2A Quickstart (Consuming)**](./quickstart-consuming-typescript.md): Learn how your agent can use other agents using the A2A Protocol.
- [**Function tools**](../tools-custom/function-tools.md): every tool you add shows up as a new skill in the agent card.
