# Quickstart: Consuming a remote agent via A2A

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-typescript">TypeScript v1.5.0</span><span class="lst-preview">Experimental</span>
</div>

An A2A agent runs somewhere else — another process, another machine, another team's
service — and speaks the [Agent2Agent protocol](intro.md) over HTTP. This page answers the
first question you hit when you meet one: **how do I call it from my ADK TypeScript agent
and get a real answer back?**

You will build two things, because they are different jobs: a script that calls a remote
agent **directly**, and a local agent that has the remote agent as a **sub-agent**, so the
model decides when to route to it. You will also start the remote agent yourself, so
nothing on this page depends on someone else's server being up.

Here is the whole direct client. This is the complete file — the only thing missing is a
remote agent to point it at, which you start in step 4.

```typescript title="examples/typescript/a2a_basic/direct_client.ts"
--8<-- "examples/typescript/a2a_basic/direct_client.ts:full"
```

Let's take a look at what is happening in this code:

1. **`new RemoteA2AAgent({...})`** is the client. It is imported from `@google/adk` — there
   is no `@google/adk/a2a` subpath — and it extends `BaseAgent`, so anywhere ADK accepts an
   agent, it accepts this.
2. **`agentCard: 'http://localhost:8001'` is a base URL, not the URL of the card.**
   `RemoteA2AAgent` appends `.well-known/agent-card.json` itself. Passing the card URL is
   the most common way to break this page; see [Troubleshooting](#troubleshooting).
3. **`name` and `description`** are required by ADK, not fetched from the remote card. The
   `description` is what a parent agent's model reads when deciding whether to route here,
   so write it for that audience.
4. **`Runner`** drives the agent exactly as it drives a local one: `runAsync()` returns an
   async iterable of events. There is no separate "A2A client" API to learn.
5. **`event.errorMessage`** is how remote failures arrive. They are *not* thrown, and the
   process still exits `0`. A loop that only reads `event.content` shows you nothing but
   your own prompt when the remote agent fails.
6. **`event.partial`** marks the streamed chunks of an answer that is still being written.
   Skipping them prints the finished sentence once. Drop that line and the same run prints
   `Yes, 7 is a`, then ` prime number.`, then `Yes, 7 is a prime number.` again.

## What you are building

- **`prime_agent`** — an `LlmAgent` with a `check_prime` tool, published over A2A. It runs
  in its own Node process and makes its own model calls.
- **`direct_client.ts`** — points a `RemoteA2AAgent` at it and asks one question.
- **`consuming_agent.ts`** — a local `root_agent` whose sub-agents are a local `roll_agent`
  and the remote `prime_agent`. The model routes between them.

!!! info "When to use `RemoteA2AAgent` — and when not to"

    Use `RemoteA2AAgent` when the thing you want to call is an agent you do not run in your
    own process: another team's service, a vendor's agent, a deployment you scale
    separately. A2A buys you a process boundary, and charges you an HTTP hop plus a
    JSON-RPC envelope for it.

    If the capability you want is a function or an HTTP API in your own codebase, define a
    [function tool](../tools-custom/function-tools.md) instead — no protocol required. If
    you want *other* people to call your agent, you want
    [A2A Quickstart (Exposing)](quickstart-exposing-typescript.md).

## Prerequisites

- **Node.js 22 or later.** Everything on this page was run on Node v22.22.2 with npm 9.2.0.
  `@google/adk` publishes no `engines` field, so npm will not warn you on an older runtime —
  but the examples use ESM and top-level `await`, which need a current Node.
- **Credentials for Gemini.** Either a Gemini API key from
  [Google AI Studio](https://aistudio.google.com/apikey), or a Google Cloud project with the
  Vertex AI API enabled and `gcloud auth application-default login` already run. Step 3 gives
  the literal `.env` for both.
- **The exact file is `.env`**, in the same directory as `package.json`. The two examples on
  this page that need it load it with `dotenv`, which reads that filename and no other.

!!! note "Which process needs the key"

    The **remote agent** (step 4) always needs it — it owns the model call. The **direct
    client** (step 6) needs no credentials at all; that is the point of A2A. The **routing
    agent** (step 8) needs one too, because it runs its own model to decide where to send
    each request.

    The split is identical on Vertex AI: the two processes that call a model need
    `GOOGLE_CLOUD_PROJECT` and application default credentials, and the direct client still
    needs nothing. `direct_client.ts` does not even import `dotenv`.

## Call a remote agent directly

### 1. Get the example code { #get-the-example-code }

Three runnable files, and the two config files they need:

```text
a2a_basic/
├── remote_prime_agent.ts   # the remote agent, served over A2A on port 8001
├── direct_client.ts        # calls it directly
├── consuming_agent.ts      # routes to it from a local agent
├── package.json
├── tsconfig.json
├── README.md
└── remote_a2a/
    └── dice_agent/         # the *other* quickstart's servers — not used here
        ├── server.ts
        └── server-with-auth.ts
```

`a2a_basic/` is shared with
[A2A Quickstart (Exposing)](quickstart-exposing-typescript.md); `remote_a2a/dice_agent/` is
that page's code and you can ignore it here, other than to note that it listens on port 8001
too, so do not run both quickstarts at once. Everything else except `README.md` is reproduced
in full on this page, so you can either clone the files or paste them.

=== "Clone them"

    ```bash
    git clone https://github.com/google/adk-docs.git
    cd adk-docs/examples/typescript/a2a_basic
    ```

    `a2a_basic/` was added to `adk-docs` alongside this page. If `cd` fails with
    `No such file or directory`, your clone predates it — `git pull`, or use the other tab.

=== "Paste them"

    ```bash
    mkdir a2a_basic && cd a2a_basic
    ```

    Then create each file as you reach it: `package.json` and `tsconfig.json` in step 2,
    `remote_prime_agent.ts` in step 4, `direct_client.ts` (shown in full at the top of this
    page) in step 6, `consuming_agent.ts` in step 7. `README.md` and `remote_a2a/` are not
    needed to run anything on this page.

### 2. Install the dependencies { #install-the-dependencies }

Both config files in full. `"type": "module"` and `"module": "nodenext"` are what allow the
top-level `await` the examples use:

```json title="examples/typescript/a2a_basic/package.json"
--8<-- "examples/typescript/a2a_basic/package.json"
```

```json title="examples/typescript/a2a_basic/tsconfig.json"
--8<-- "examples/typescript/a2a_basic/tsconfig.json"
```

The `serve:dice` scripts and the `remote_a2a/**/*.ts` entry in `include` belong to
[A2A Quickstart (Exposing)](quickstart-exposing-typescript.md), which shares this directory.
This page uses `serve:prime`, `direct`, and `consume`; if you are pasting the files rather
than cloning them, drop the two `serve:dice` lines and the `remote_a2a` include.

Then install:

=== "npm"

    ```bash
    npm install @google/adk zod dotenv
    npm install --save-dev typescript tsx @types/node
    ```

=== "pnpm"

    ```bash
    pnpm add @google/adk zod dotenv
    pnpm add --save-dev typescript tsx @types/node
    ```

=== "yarn"

    ```bash
    yarn add @google/adk zod dotenv
    yarn add --dev typescript tsx @types/node
    ```

`@google/adk` brings the A2A stack with it: both the A2A SDK (`@a2a-js/sdk`) and Express are
direct dependencies of the package, not peer dependencies, so there is nothing else to
install to make A2A work. `zod` defines the tool's input schema, and `dotenv` loads `.env`.
Keep `zod` on **v4**: `@google/adk@1.5.0` depends on `zod@^4.2.1`, and a `zod@3` in your own
`package.json` puts two incompatible copies in `node_modules`, after which `tsc` rejects
every tool schema you write.

### 3. Add your credentials { #add-your-credentials }

Pick the backend you have access to. Either way the file is `.env`, next to `package.json`,
and this is its entire contents:

=== "Gemini API key"

    ```bash title="examples/typescript/a2a_basic/.env"
    GOOGLE_GENAI_API_KEY=your-api-key-here
    ```

    Replace `your-api-key-here` with a key from
    [Google AI Studio](https://aistudio.google.com/apikey). ADK reads `GOOGLE_GENAI_API_KEY`
    or `GEMINI_API_KEY`, in that order — and **not** `GOOGLE_API_KEY`.

=== "Vertex AI"

    ```bash title="examples/typescript/a2a_basic/.env"
    GOOGLE_GENAI_USE_VERTEXAI=true
    GOOGLE_CLOUD_PROJECT=your-project-id
    GOOGLE_CLOUD_LOCATION=global
    ```

    No key. Credentials come from application default credentials, so run this once:

    ```bash
    gcloud auth application-default login
    ```

    `GOOGLE_GENAI_USE_VERTEXAI=true` is what switches backends; without it ADK looks for an
    API key and ignores the project. `global` works for `GOOGLE_CLOUD_LOCATION` unless you
    need a specific region. To confirm you are on this path, watch for
    `backend: VERTEX_AI` in the `INFO: [ADK] … Sending out request` line each model call
    prints — it says `backend: GEMINI_API` on the API-key path.

Get this wrong and the two halves fail in ways that look nothing alike. The **remote agent**
does not throw: it packages the failure into its A2A reply, so your client prints an error
event and still exits `0`. The **routing agent** builds its model in-process and really does
throw, with exit `1`. Both are in [Troubleshooting](#troubleshooting).

### 4. Start the remote agent { #start-the-remote-agent }

This is the agent your client will call. It is an ordinary `LlmAgent`; `toA2a()` is the only
A2A-specific line.

```typescript title="examples/typescript/a2a_basic/remote_prime_agent.ts"
--8<-- "examples/typescript/a2a_basic/remote_prime_agent.ts:full"
```

Let's take a look at what is happening in this code:

1. **`checkPrime`** is a plain `FunctionTool`. Its `parameters` are a `z.object({ numbers:
   z.array(z.number()) })`, and that schema is what types the `{ numbers }` destructured in
   `execute` — `numbers` is a `number[]` with no annotation written by hand.
2. **`primeAgent`** is an `LlmAgent` like any other. Nothing about it is written for A2A.
3. **`toA2a(primeAgent, {...})`** returns an `express.Application`. It is `await`ed because
   it builds the agent card asynchronously.
4. **`allowUnauthenticated: true`** is mandatory here and local-only: without it `toA2a()`
   throws and refuses to mount, because an unauthenticated A2A endpoint lets any caller that
   can reach the port invoke the agent and its tools. It logs a loud `SECURITY WARNING` when
   you use it.
5. **`app.listen(PORT)`** is yours to call. `toA2a()` never starts a server — its `port`
   option only decorates the agent card, so the two must agree.

Run it, and leave it running:

```bash
npx tsx remote_prime_agent.ts
```

```text
WARN: [ADK] 2026-08-05T17:27:54.112Z SECURITY WARNING: Mounting the A2A server WITHOUT authentication because `allowUnauthenticated: true` was set. The agent and all of its tools are exposed to any network-reachable caller, which can invoke them with arbitrary input and read the output. Do NOT use this outside of local, trusted development.
(node:4058702) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
(Use `node --trace-deprecation ...` to show where the warning was created)
[server] prime_agent listening on http://localhost:8001
[server] agent card: http://localhost:8001/.well-known/agent-card.json
```

Those two `punycode` lines come from a transitive dependency and are harmless. Node 22 prints
them on **every** command on this page; the later transcripts leave them out, along with the
`INFO: [ADK] … Sending out request, model: gemini-2.5-flash …` line each model call emits.
Extra Node warning lines do not mean you have gone wrong.

### 5. Confirm the agent card is being served { #confirm-the-agent-card }

Every A2A agent publishes a card describing what it can do, and that card is what
`RemoteA2AAgent` fetches first. ADK generates it from your agent — you never write it by
hand:

```bash
curl -s http://localhost:8001/.well-known/agent-card.json
```

```json
{
    "name": "prime_agent",
    "description": "Checks whether numbers are prime.",
    "protocolVersion": "0.3.0",
    "version": "1.0.0",
    "skills": [
        {
            "id": "prime_agent",
            "name": "model",
            "description": "Checks whether numbers are prime. I check whether numbers are prime. Always call the check_prime tool, then answer in one short sentence.",
            "tags": ["llm"]
        },
        {
            "id": "prime_agent-check_prime",
            "name": "check_prime",
            "description": "Checks which numbers in a list are prime.",
            "tags": ["llm", "tools"]
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
    "defaultInputModes": ["text"],
    "defaultOutputModes": ["text"],
    "additionalInterfaces": [
        {"url": "http://localhost:8001/jsonrpc", "transport": "JSONRPC"},
        {"url": "http://localhost:8001/rest", "transport": "HTTP+JSON"}
    ]
}
```

Two things to notice, because both surprise people the first time:

- Your instruction `"You check whether numbers are prime"` is published as `"I check
  whether numbers are prime"`. Card descriptions are rewritten into the first person on
  purpose.
- `capabilities.streaming` is `true`, so `RemoteA2AAgent` will use the streaming transport.
  That is where the `event.partial` chunks in step 6 come from.

### 6. Point a client at it and run { #point-a-client-at-it-and-run }

The client is `direct_client.ts`, shown in full at the top of this page. The part that
matters is one constructor call:

```typescript title="examples/typescript/a2a_basic/direct_client.ts"
--8<-- "examples/typescript/a2a_basic/direct_client.ts:remote-agent"
```

In a second terminal:

```bash
npx tsx direct_client.ts
```

```text
user > Is 7 a prime number?
prime_agent > Yes, 7 is a prime number.
```

That answer came out of the other process. Look at the terminal running
`remote_prime_agent.ts` and you will see the tool that produced it actually executed there:

```text
[server] check_prime(7) -> 7
```

You now have a working A2A call, and the client that made it holds no API key.

## Route to the remote agent from a local agent

Calling a remote agent directly is useful when you already know you want it. The more
interesting shape is handing it to a model as one option among several: because
`RemoteA2AAgent` extends `BaseAgent`, it drops into `subAgents` and ADK's routing treats it
like any local sub-agent.

### 7. Add a root agent with the remote agent as a sub-agent { #add-a-root-agent }

```typescript title="examples/typescript/a2a_basic/consuming_agent.ts"
--8<-- "examples/typescript/a2a_basic/consuming_agent.ts:imports"

--8<-- "examples/typescript/a2a_basic/consuming_agent.ts:roll-agent"

--8<-- "examples/typescript/a2a_basic/consuming_agent.ts:remote-agent"

--8<-- "examples/typescript/a2a_basic/consuming_agent.ts:root-agent"
```

Let's take a look at what is happening in this code:

1. **`rollAgent`** is a local `LlmAgent` with a local `roll_die` tool. It runs in this
   process.
2. **`primeAgent`** is the same `RemoteA2AAgent` as before, unchanged. Nothing about
   composition requires a different construction.
3. **`subAgents: [rollAgent, primeAgent]`** mixes local and remote freely. `rootAgent`'s
   model sees both and emits a `transfer_to_agent` call to pick one; ADK turns that into an
   A2A request when the target is remote.
4. **`description`** on `primeAgent` is doing real work now — it is the text the routing
   model reads to decide that "is this prime?" belongs to `prime_agent`.

The loop that prints the run is the same one from `direct_client.ts`, plus one branch so
you can watch the routing happen:

```typescript title="examples/typescript/a2a_basic/consuming_agent.ts"
--8<-- "examples/typescript/a2a_basic/consuming_agent.ts:run"
```

`part.functionCall` catches both the `transfer_to_agent` handoffs and the tool calls the
remote agent makes on its own side, which stream back to you as ordinary events.

### 8. Run it { #run-it }

With `remote_prime_agent.ts` still running in the first terminal:

```bash
npx tsx consuming_agent.ts
```

```text
user > Roll a 6-sided die and tell me whether the result is prime.
root_agent calls transfer_to_agent({"agentName":"roll_agent"})
roll_agent calls roll_die({"sides":6})
roll_agent > The result of your 6-sided die roll is 6.
roll_agent calls transfer_to_agent({"agentName":"prime_agent"})
prime_agent calls check_prime({"numbers":[6]})
prime_agent > 6 is not a prime number.
```

Read that trace bottom-up and you can see the whole point: `check_prime({"numbers":[6]})`
was decided by a model in *your* process, executed by a tool in a *different* process, and
the sentence came back over A2A as an event your loop printed. The remote terminal confirms
its half:

```text
[server] check_prime(6) -> none
```

**Compare the shape, not the words.** The four `calls` lines are the same on every run, in
that order; that is the part worth checking. The two `>` lines are model prose and will be
worded differently for you. Across eight consecutive runs here the four `calls` lines were
identical eight times and the two sentences never were: `roll_agent` said
`I rolled a 5.`, `The result of your 6-sided die roll is 6.` and
`I rolled a 6-sided die and got 2.`, and `prime_agent` answered `Yes, 5 is prime.`,
`4 is not prime.` and `2 is a prime number.` Do not diff this transcript character by
character.

Routing is still a model decision, and it can go wrong: given a vaguer instruction,
`roll_agent` sometimes handed straight back to `root_agent` without rolling and the run
ended with `root_agent` asking what the number was — no A2A call at all. That is what the
`Never transfer to another agent before you have reported a number` clause in `roll_agent`'s
instruction is for.

## Troubleshooting

### `Failed to fetch Agent Card from …/.well-known/.well-known/agent-card.json: 404`

You passed the **card URL** as `agentCard` instead of the **base URL**. The resolver appends
`.well-known/agent-card.json` to whatever you give it, so the path doubles. This one does
not surface as an error event — it takes the process down:

```text
Error: Failed to fetch Agent Card from http://localhost:8001/.well-known/.well-known/agent-card.json: 404
    at DefaultAgentCardResolver.resolve (…/@a2a-js/sdk/dist/client/index.js:723:13)
    at async resolveAgentCard (…/@google/adk/dist/esm/a2a/agent_card.js:28:12)
    at async RemoteA2AAgent.init (…/@google/adk/dist/esm/a2a/a2a_remote_agent.js:43:19)

Node.js v22.22.2
```

Card resolution happens before the error handling that produces `event.errorMessage`, which
is why this crashes when every other remote failure does not.

```typescript
// Wrong — 404s and exits.
agentCard: 'http://localhost:8001/.well-known/agent-card.json',

// Right.
agentCard: 'http://localhost:8001',
```

The same trap has a second form. If the remote agent was mounted under a `basePath`, your
base URL needs a **trailing slash**, because `new URL()` drops the last segment without one:

```text
http://localhost:8001/a2a   ->  http://localhost:8001/.well-known/agent-card.json      # "a2a" silently dropped
http://localhost:8001/a2a/  ->  http://localhost:8001/a2a/.well-known/agent-card.json  # correct
```

### `TypeError: fetch failed`

Nothing answered at the address. Two different causes, and the difference is where it
appears:

- **Your `agentCard` URL points at a port nothing is listening on.** The card fetch itself
  fails, so it crashes the process the same way the 404 above does, with
  `[cause]: AggregateError [ECONNREFUSED]`. Check the port in `agentCard` against the one
  the remote terminal printed.
- **The card resolved, but the URL inside it is dead.** This one arrives as an error event:

    ```text
    ERROR: [ADK] 2026-08-05T18:41:10.405Z A2ARemoteAgent prime_agent failed: TypeError: fetch failed
    [error] prime_agent: fetch failed
    ```

    That means the remote server's `toA2a({ port })` and its `app.listen(port)` disagree.
    `toA2a`'s `port` only writes the `"url"` field of the agent card; it starts nothing. If
    they differ, the card fetch succeeds and every RPC afterwards goes to a port with no
    server on it.

### The client prints your prompt, then almost nothing, and exits 0

Your event loop reads `event.content` but never `event.errorMessage`. Remote failures do not
throw and do not produce content, so a loop like this shows you a near-empty screen:

```typescript
for await (const event of runner.runAsync({ /* ... */ })) {
  // Nothing here will ever run when the remote agent fails.
  for (const part of event.content?.parts ?? []) {
    if (part.text) console.log(part.text);
  }
}
```

You are not left with *nothing*, but with almost nothing, and only for some failures.
A transport failure gets one line out of ADK's own logger before the silence:

```text
user > Is 7 a prime number?
ERROR: [ADK] 2026-08-05T18:41:14.373Z A2ARemoteAgent prime_agent failed: TypeError: fetch failed
```

A failure *inside* the remote agent — a bad model call, a throwing tool — prints nothing at
all. Either way the exit code is `0`.

Always check `errorMessage` first, as `direct_client.ts` does:

```typescript
if (event.errorMessage) {
  console.error(`[error] ${event.author}: ${event.errorMessage}`);
  continue;
}
```

### `500 Internal Server Error. RPC Error: General processing error. (Code: -32603)`

The remote agent is authenticated and rejected you. The full event text is:

```text
[error] prime_agent: HTTP error establishing stream for message/stream: 500 Internal Server Error. RPC Error: General processing error. (Code: -32603)
```

**Do not go looking for a 401.** A rejected A2A request comes back as HTTP 500 with JSON-RPC
code `-32603` and no hint that credentials were the problem. Confusing matters further, the
agent card endpoint is *never* authenticated — only `/jsonrpc` and `/rest` are — so
`curl`ing the card returns `200` even when every call you make is being refused.

`RemoteA2AAgent` has no token option, so there is nowhere obvious to put a credential.
Attaching one means replacing the client's transport:

??? note "Sending an Authorization header from a RemoteA2AAgent"

    Swap the `primeAgent` constant in `direct_client.ts` for the version below. Only the
    `@a2a-js/sdk/client` import is new — `RemoteA2AAgent` is already imported at the top of
    that file.

    ```typescript title="examples/typescript/a2a_basic/direct_client.ts"
    import {
      ClientFactory,
      ClientFactoryOptions,
      JsonRpcTransportFactory,
    } from '@a2a-js/sdk/client';

    const authFetch: typeof fetch = (input, init = {}) =>
      fetch(input, {
        ...init,
        headers: { ...(init.headers ?? {}), Authorization: `Bearer ${process.env.A2A_TOKEN}` },
      });

    const primeAgent = new RemoteA2AAgent({
      name: 'prime_agent',
      description: 'Remote agent that checks whether numbers are prime.',
      agentCard: 'http://localhost:8001',
      clientFactory: new ClientFactory(
        ClientFactoryOptions.createFrom(ClientFactoryOptions.default, {
          transports: [new JsonRpcTransportFactory({ fetchImpl: authFetch })],
        }),
      ),
    });
    ```

    Add `@a2a-js/sdk` to your own `package.json` if you import from it like this. It resolves
    today through `@google/adk`'s own dependency tree, but that is npm hoisting doing you a
    favour, and pnpm will not.

### `[error] prime_agent: Agent run failed: API key must be provided …`

The **remote agent** has no credentials. This is the one people expect to throw, and it does
not:

```text
user > Is 7 a prime number?
[error] prime_agent: Agent run failed: API key must be provided via constructor or GOOGLE_GENAI_API_KEY or GEMINI_API_KEY environment variable.
```

Exit code `0`, and the remote terminal logs nothing at all — the error is packaged into the
A2A response instead. Check that `.env` exists next to `package.json` **in the directory you
started the remote agent from** (see [step 3](#add-your-credentials)).

The local agents are the opposite. `consuming_agent.ts` builds its own model in-process, so
missing credentials there really do throw — same message, but as an uncaught
`Error:` whose first stack frame is `at new Gemini (…/models/google_llm.js:52:13)`, and
exit `1`.

### A ~30-line JSON dump starting `[error] prime_agent: {`

The remote agent's key exists but is **wrong**. The provider's raw error is passed through
verbatim, so it does not look like an ADK message at all:

```text
[error] prime_agent: {
  "error": {
    "code": 400,
    "message": "API key not valid. Please pass a valid API key.",
    "status": "INVALID_ARGUMENT",
    …
```

Exit code `0` again. Twenty or so more lines of `details` follow, ending with a
`DebugInfo` entry that echoes the key you actually sent — worth reading, because it is
usually a truncated paste or a stale key rather than the one in `.env`.

## Next steps

- **Let other agents call the agent you just wrote** —
  [A2A Quickstart (Exposing)](quickstart-exposing-typescript.md) covers `toA2a()`,
  authentication that is not `allowUnauthenticated`, and what ends up in your agent card.
- **Understand what is actually on the wire** —
  [Introduction to A2A](intro.md) walks through agent cards, tasks, and the JSON-RPC
  messages your client is exchanging.
- **Give the routing model something local to choose instead** — define a
  [function tool](../tools-custom/function-tools.md) so `root_agent` can answer some
  requests itself rather than delegating every one of them.
- **Hand the remote agent to a model as a tool rather than a destination** —
  [Agent-as-a-Tool](../tools-custom/function-tools.md#agent-tool) wraps an agent — and a
  `RemoteA2AAgent` is a `BaseAgent` like any other — so the caller gets the answer back and
  keeps control instead of transferring away.
