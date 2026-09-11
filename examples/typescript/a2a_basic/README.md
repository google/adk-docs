# A2A basic example (ADK TypeScript)

Companion code for the two TypeScript A2A quickstarts. They are two halves of the same
story — one agent publishes itself over A2A, another agent calls one — so they share this
directory:

- [A2A Quickstart (Exposing)](https://google.github.io/adk-docs/a2a/quickstart-exposing-typescript/)
  — put an agent behind `toA2a()` and call it with `curl`.
- [A2A Quickstart (Consuming)](https://google.github.io/adk-docs/a2a/quickstart-consuming-typescript/)
  — call a remote agent with `RemoteA2AAgent`, directly and as a sub-agent.

Every server here listens on `http://localhost:8001`, so **run one at a time**.

## Files

| File | What it is | Page |
|---|---|---|
| `remote_a2a/dice_agent/server.ts` | A dice-rolling `LlmAgent` published with `toA2a()`. Uses `allowUnauthenticated: true`, which is for local development only. | Exposing |
| `remote_a2a/dice_agent/server-with-auth.ts` | The same agent behind a bearer-token `UserBuilder` — what you want anywhere other than localhost. | Exposing |
| `remote_prime_agent.ts` | The remote agent for the consuming page: an `LlmAgent` with a `check_prime` tool, published with `toA2a()`. Start this before either client. | Consuming |
| `direct_client.ts` | Calls `remote_prime_agent.ts` directly with `RemoteA2AAgent` + `Runner`. Needs no credentials — the remote side owns the model call. | Consuming |
| `consuming_agent.ts` | A local `root_agent` whose sub-agents are a local `roll_agent` and the remote `prime_agent`. The model decides which one handles each request. | Consuming |

The `remote_a2a/dice_agent/` layout mirrors the Python and Go `a2a_basic` samples; the
consuming files sit flat because that page builds them one at a time.

## Setup

```bash
npm install
```

Create a `.env` file next to `package.json`. Either a Gemini API key:

```bash
GOOGLE_GENAI_API_KEY=your-api-key-here
```

Get one at [Google AI Studio](https://aistudio.google.com/apikey). ADK reads
`GOOGLE_GENAI_API_KEY` or `GEMINI_API_KEY` — and **not** `GOOGLE_API_KEY`. Or use Vertex AI,
with `gcloud auth application-default login` already run:

```bash
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=global
```

`server-with-auth.ts` needs one more line, the shared secret it checks. Keep it in `.env`
rather than on the command line, where it would be visible to `ps` and saved in your shell
history:

```bash
A2A_SHARED_TOKEN=s3cret-token
```

How each file finds `.env` differs, and the scripts below already do the right thing:
`remote_prime_agent.ts` and `consuming_agent.ts` import `dotenv/config` and load it
themselves; the two dice servers do not, so their scripts pass Node's `--env-file=.env`.
`direct_client.ts` needs no credentials at all.

## Run

Every command that starts a process is an npm script, so nothing depends on where `tsx` is
installed. The comment after each one shows what it runs.

### Exposing

```bash
npm run serve:dice        # tsx --env-file=.env remote_a2a/dice_agent/server.ts
```

Then, in a second terminal, fetch the agent card and send a request:

```bash
curl -s http://localhost:8001/.well-known/agent-card.json | jq

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
  }' | jq -c '.result.status.state, .result.artifacts[-1].parts[0].text'
```

A successful response is a task with `"state": "completed"` whose last artifact holds the
agent's answer, for example `"You rolled a 17."`.

For the authenticated variant:

```bash
npm run serve:dice:auth   # tsx --env-file=.env remote_a2a/dice_agent/server-with-auth.ts
```

Send the same request with `-H 'Authorization: Bearer s3cret-token'`. Without the header, or
with the wrong token, you get JSON-RPC error `-32603` and HTTP 500 — not a 401. The agent
card endpoint stays public either way.

### Consuming

Terminal 1 — the remote agent:

```bash
npm run serve:prime       # tsx remote_prime_agent.ts
```

Terminal 2 — call it directly:

```bash
npm run direct            # tsx direct_client.ts
```

```text
user > Is 7 a prime number?
prime_agent > Yes, 7 is a prime number.
```

Terminal 2 — or let a local agent route to it:

```bash
npm run consume           # tsx consuming_agent.ts
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

The four `calls` lines are the same every run. The number and the wording of the two `>`
sentences are not — they are model output.

## Typecheck

```bash
npm run typecheck         # tsc --noEmit
```

This covers both layouts: `include` in `tsconfig.json` lists `*.ts` and
`remote_a2a/**/*.ts`.

## Notes

- Every server passes `allowUnauthenticated: true` except `server-with-auth.ts`. That is for
  local development only: without it, and without an `authentication` callback, `toA2a()`
  refuses to mount.
- `toA2a()`'s `port` option only writes the URL into the agent card — it opens no socket.
  It has to agree with the port you pass to `app.listen()`.
- `agentCard` on `RemoteA2AAgent` is a **base URL**, not the URL of the card.
  Passing `http://localhost:8001/.well-known/agent-card.json` requests
  `/.well-known/.well-known/agent-card.json`, 404s, and crashes the process.
- Keep `zod` on **v4**. `@google/adk@1.5.0` depends on `zod@^4.2.1`; a `zod@3` in this
  `package.json` puts two incompatible copies in `node_modules` and `tsc` then rejects every
  tool schema here.
