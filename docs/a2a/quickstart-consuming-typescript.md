# Quickstart: Consuming a remote agent via A2A

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-typescript">TypeScript</span><span class="lst-preview">Experimental</span>
</div>

This quickstart covers the most common starting point for any developer: **"There is a remote agent, how do I let my ADK agent use it via A2A?"**. This is crucial for building complex multi-agent systems where different agents need to collaborate and interact.

## Overview

This sample demonstrates the **Agent2Agent (A2A)** architecture in the Agent Development Kit (ADK), showcasing how multiple agents can work together to handle complex tasks. The sample implements an agent that can roll dice and check if numbers are prime.

```text
┌─────────────────┐    ┌──────────────────┐    ┌────────────────────┐
│   Root Agent    │───▶│   Roll Agent     │    │   Remote Prime     │
│  (Local)        │    │   (Local)        │    │   Agent            │
│                 │    │                  │    │  (localhost:8001)  │
│                 │───▶│                  │◀───│                    │
└─────────────────┘    └──────────────────┘    └────────────────────┘
```

The A2A Basic sample consists of:

- **Remote Prime Agent** (`remote_prime_agent.ts`): An `LlmAgent` with a `check_prime` tool, published over A2A. It runs in its own Node process and makes its own model calls.
- **Direct client** (`direct_client.ts`): Points a `RemoteA2AAgent` straight at the remote agent and asks one question. It holds no credentials.
- **Routing agent** (`consuming_agent.ts`): A local `root_agent` whose sub-agents are a local `roll_agent` and the remote `prime_agent`. The model decides which one handles each request.

Use `RemoteA2AAgent` when the thing you want to call is an agent you do not run in your own process: another team's service, a vendor's agent, a deployment you scale separately. A2A buys you a process boundary and charges you an HTTP hop plus a JSON-RPC envelope for it. If the capability you want is a function or an HTTP API in your own codebase, define a [function tool](../tools-custom/function-tools.md) instead. Everything below was run on **Node.js 22** — `@google/adk` publishes no `engines` field, so npm will not warn you on an older runtime, but the examples use ESM and top-level `await`.

## Exposing Your Agent with the ADK Server

In TypeScript you expose an agent with `toA2a()`, which auto-generates its agent card and returns an Express application you serve yourself. It is covered in full by [A2A Quickstart (Exposing)](quickstart-exposing-typescript.md).

In the `a2a_basic` example, you will first need to expose the `prime_agent` via an A2A server, so that the local root agent can use it.

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
├── remote_prime_agent.ts   # the remote agent, served over A2A on port 8001
├── direct_client.ts        # calls it directly
├── consuming_agent.ts      # routes to it from a local agent
├── package.json
├── tsconfig.json
├── README.md
└── remote_a2a/
    └── dice_agent/         # A2A Quickstart (Exposing) uses these
```

`a2a_basic/` is shared with [A2A Quickstart (Exposing)](quickstart-exposing-typescript.md); `remote_a2a/dice_agent/` is that page's code, and it listens on port 8001 too, so do not run both quickstarts at once.

#### Main Agents (`a2a_basic/direct_client.ts`, `a2a_basic/consuming_agent.ts`)

- **`primeAgent`**: The `RemoteA2AAgent` configuration — a `name`, a `description`, and the base URL of the remote agent's card.
- **`rollDie` / `rollAgent`**: A local function tool and the local agent that owns it.
- **`rootAgent`**: Main orchestrator with delegation logic, mixing the local and remote sub-agents.

#### Remote Prime Agent (`a2a_basic/remote_prime_agent.ts`)

- **`checkPrime`**: Prime number checking algorithm, wrapped as a `FunctionTool`.
- **`toA2a(primeAgent, {...})`**: Publishes the agent and auto-generates its agent card.

`@google/adk` brings the A2A stack with it: both the A2A SDK (`@a2a-js/sdk`) and Express are direct dependencies of the package, not peer dependencies, so there is nothing else to install to make A2A work. `zod` defines the tool's input schema and `dotenv` loads `.env`. Keep `zod` on **v4** — `@google/adk` depends on `zod@^4.2.1`, and a `zod@3` in your own `package.json` puts two incompatible copies in `node_modules`, after which `tsc` rejects every tool schema you write.

Then add your model credentials. Either way the file is `.env`, next to `package.json`, and this is its entire contents:

=== "Gemini API key"

    ```bash title="a2a_basic/.env"
    GOOGLE_GENAI_API_KEY=your-api-key-here
    ```

    Replace `your-api-key-here` with a key from
    [Google AI Studio](https://aistudio.google.com/apikey). ADK reads `GOOGLE_GENAI_API_KEY`
    or `GEMINI_API_KEY`, in that order — and **not** `GOOGLE_API_KEY`.

=== "Vertex AI"

    ```bash title="a2a_basic/.env"
    GOOGLE_GENAI_USE_VERTEXAI=true
    GOOGLE_CLOUD_PROJECT=your-project-id
    GOOGLE_CLOUD_LOCATION=global
    ```

    No key. Credentials come from application default credentials, so run
    `gcloud auth application-default login` once. `GOOGLE_GENAI_USE_VERTEXAI=true` is what
    switches backends; without it ADK looks for an API key and ignores the project. `global`
    works for `GOOGLE_CLOUD_LOCATION` unless you need a specific region. To confirm you are on
    this path, watch for `backend: VERTEX_AI` in the `INFO: [ADK] … Sending out request` line
    each model call prints — it says `backend: GEMINI_API` on the API-key path.

!!! note "Which process needs the credentials"

    The **remote agent** always needs them — it owns the model call. The **routing agent** needs
    them too, because it runs its own model to decide where to send each request. The **direct
    client** needs none at all; that is the point of A2A, and `direct_client.ts` does not even
    import `dotenv`.

### 2. Start the Remote Prime Agent server { #start-the-remote-prime-agent-server }

To show how your ADK agent can consume a remote agent via A2A, you'll first need to start a remote agent server, which will host the prime agent. It is an ordinary `LlmAgent`; `toA2a()` is the only A2A-specific line, and `app.listen()` is yours to call because `toA2a()`'s `port` option only decorates the agent card.

```typescript title="a2a_basic/remote_prime_agent.ts"
--8<-- "examples/typescript/a2a_basic/remote_prime_agent.ts:full"
```

Run it, and leave it running:

```bash
npx tsx remote_prime_agent.ts    # or: npm run serve:prime
```

Once executed, you should see something like:

```console
WARN: [ADK] 2026-08-06T21:17:35.200Z SECURITY WARNING: Mounting the A2A server WITHOUT authentication because `allowUnauthenticated: true` was set. The agent and all of its tools are exposed to any network-reachable caller, which can invoke them with arbitrary input and read the output. Do NOT use this outside of local, trusted development.
(node:2816572) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
(Use `node --trace-deprecation ...` to show where the warning was created)
[server] prime_agent listening on http://localhost:8001
[server] agent card: http://localhost:8001/.well-known/agent-card.json
```

`allowUnauthenticated: true` is mandatory here and local-only: without it `toA2a()` refuses to mount, because an unauthenticated A2A endpoint lets any caller that can reach the port invoke the agent and its tools. The two `punycode` lines come from a transitive dependency and are harmless — Node 22 prints them on **every** command on this page, and the later transcripts leave them out along with the `INFO: [ADK] … Sending out request` line each model call emits.

!!! note "The remote agent's failures arrive as events, not exceptions"

    If the remote agent has no credentials, or the wrong ones, it does not throw: it packages
    the failure into its A2A reply, your client prints an error event, and the process still
    exits `0`. The remote terminal logs nothing at all. So check that `.env` exists next to
    `package.json` **in the directory you started the remote agent from**. Local agents are the
    opposite — `consuming_agent.ts` builds its model in-process, so missing credentials there
    really do throw, with exit `1`.

### 3. Look out for the required agent card of the remote agent { #look-out-for-the-required-agent-card-of-the-remote-agent }

A2A Protocol requires that each agent must have an agent card that describes what it does, and that card is what `RemoteA2AAgent` fetches first.

In the TypeScript ADK, the agent card is generated dynamically when you expose an agent with `toA2a()` — you never write it by hand. You can visit `http://localhost:8001/.well-known/agent-card.json` to see the generated card:

```bash
curl -s http://localhost:8001/.well-known/agent-card.json \
  | jq '{name, url, capabilities, skills: [.skills[] | {name, description}]}'
```

```json
{
  "name": "prime_agent",
  "url": "http://localhost:8001/jsonrpc",
  "capabilities": {
    "extensions": [],
    "stateTransitionHistory": false,
    "pushNotifications": false,
    "streaming": true
  },
  "skills": [
    {
      "name": "model",
      "description": "Checks whether numbers are prime. I check whether numbers are prime. Always call the check_prime tool, then answer in one short sentence."
    },
    {
      "name": "check_prime",
      "description": "Checks which numbers in a list are prime."
    }
  ]
}
```

Two things to notice, because both surprise people the first time. Your instruction `"You check whether numbers are prime"` is published as `"I check whether numbers are prime"` — card descriptions are rewritten into the first person on purpose. And `capabilities.streaming` is `true`, so `RemoteA2AAgent` uses the streaming transport; that is where the partial events in step 4 come from.

### 4. Run the Main (Consuming) Agent { #run-the-main-consuming-agent }

With `remote_prime_agent.ts` still running in the first terminal, call it directly:

```bash
npx tsx direct_client.ts       # or: npm run direct
```

Or let a local agent route to it:

```bash
npx tsx consuming_agent.ts     # or: npm run consume
```

#### How it works

The main agent uses `RemoteA2AAgent` to consume the remote agent (`prime_agent` in our example). It requires the `name`, the `description`, and the **base URL** of the agent card:

```typescript title="a2a_basic/direct_client.ts"
--8<-- "examples/typescript/a2a_basic/direct_client.ts:remote-agent"
```

!!! warning "`agentCard` is a base URL, not the URL of the card"

    `RemoteA2AAgent` appends `.well-known/agent-card.json` itself, so passing the card URL
    doubles the path. Card resolution happens before the error handling that produces
    `event.errorMessage`, so unlike every other remote failure this one takes the process down:
    `Error: Failed to fetch Agent Card from http://localhost:8001/.well-known/.well-known/agent-card.json: 404`.
    The same trap has a second form: if the remote agent was mounted under a `basePath`, your
    base URL needs a **trailing slash**, because `new URL()` drops the last segment without one.

    ```typescript
    agentCard: 'http://localhost:8001/.well-known/agent-card.json',  // Wrong — 404s and exits.
    agentCard: 'http://localhost:8001',                              // Right.
    ```

`RemoteA2AAgent` extends `BaseAgent`, so anywhere ADK accepts an agent it accepts this one, and a `Runner` drives it exactly as it drives a local agent — `runAsync()` returns an async iterable of events, and there is no separate "A2A client" API to learn:

```typescript title="a2a_basic/direct_client.ts"
--8<-- "examples/typescript/a2a_basic/direct_client.ts:event-loop"
```

!!! warning "Read `event.errorMessage`, or remote failures are silent"

    Remote failures are *not* thrown and the process still exits `0`. A loop that only reads
    `event.content` shows you nothing but your own prompt: a transport failure gets one line out
    of ADK's own logger (`ERROR: [ADK] … A2ARemoteAgent prime_agent failed: TypeError: fetch
    failed`) before the silence, and a failure *inside* the remote agent prints nothing at all.
    Check `errorMessage` first, as `direct_client.ts` does.

`event.partial` marks the streamed chunks of an answer that is still being written; skipping them prints the finished sentence once. Drop that line and the same run prints the answer in pieces and then again in full — on one run here, `Yes`, then `, 7 is a prime number.`, then `Yes, 7 is a prime number.` Where the chunk boundaries fall varies from run to run.

Because `RemoteA2AAgent` extends `BaseAgent`, it also drops straight into `subAgents`, and ADK's routing treats it like any local sub-agent. That is what `consuming_agent.ts` does:

```typescript title="a2a_basic/consuming_agent.ts"
--8<-- "examples/typescript/a2a_basic/consuming_agent.ts:remote-agent"

--8<-- "examples/typescript/a2a_basic/consuming_agent.ts:root-agent"
```

`subAgents: [rollAgent, primeAgent]` mixes local and remote freely. `rootAgent`'s model sees both and emits a `transfer_to_agent` call to pick one; ADK turns that into an A2A request when the target is remote. The `description` on `primeAgent` is doing real work here — it is the text the routing model reads to decide that "is this prime?" belongs to `prime_agent`.

## Example Interactions

Once both your main and remote agents are running, you can interact with the root agent to see how it calls the remote agent via A2A:

**Prime Number Checking:**

This interaction uses a remote agent via A2A, the Prime Agent. `npx tsx direct_client.ts` prints:

```text
user > Is 7 a prime number?
prime_agent > Yes, 7 is a prime number.
```

That answer came out of the other process. The terminal running `remote_prime_agent.ts` shows the tool that produced it actually executing there:

```text
[server] check_prime(7) -> 7
```

**Combined Operations:**

This interaction uses both the local Roll Agent and the remote Prime Agent. `npx tsx consuming_agent.ts` prints:

```text
user > Roll a 6-sided die and tell me whether the result is prime.
root_agent calls transfer_to_agent({"agentName":"roll_agent"})
roll_agent calls roll_die({"sides":6})
roll_agent > I rolled a 6-sided die and got 1.
roll_agent calls transfer_to_agent({"agentName":"prime_agent"})
prime_agent calls check_prime({"numbers":[1]})
prime_agent > 1 is not a prime number.
```

```text
[server] check_prime(1) -> none
```

That trace is the whole point: `check_prime` was decided by a model in *your* process, executed by a tool in a *different* process, and the sentence came back over A2A as an event your loop printed.

**Compare the shape, not the words.** The four `calls` lines are the same on every run, in that order; that is the part worth checking. The two `>` lines are model prose and will be worded differently for you — and the rolled number changes every time. Routing is a model decision and it can go wrong: given a vaguer instruction, `roll_agent` sometimes handed straight back to `root_agent` without rolling, and the run ended with no A2A call at all. That is what the `Never transfer to another agent before you have reported a number` clause in `roll_agent`'s instruction is for.

## Next Steps

Now that you have created an agent that's using a remote agent via an A2A server, the next step is to learn how to expose your own agent.

- [**A2A Quickstart (Exposing)**](quickstart-exposing-typescript.md): Learn how to expose your existing agent so that other agents can use it via the A2A Protocol, including authentication that is not `allowUnauthenticated`.
- [**Introduction to A2A**](intro.md): agent cards, tasks, and the JSON-RPC messages your client is exchanging.
- [**Agent-as-a-Tool**](../tools-custom/function-tools.md#agent-tool): wrap the remote agent as a tool rather than a destination, so the caller gets the answer back and keeps control instead of transferring away.
