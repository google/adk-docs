# A2A basic example (ADK TypeScript)

Companion code for
[Quickstart: Consuming a remote agent via A2A](https://adk.dev/a2a/quickstart-consuming-typescript/).

A remote agent is exposed over A2A on `localhost:8001`, and two clients call it:
one directly, one by routing to it from a local agent.

## Files

| File | What it is |
|---|---|
| `remote_prime_agent.ts` | The remote agent. An `LlmAgent` with a `check_prime` tool, published over A2A with `toA2a()`. Run this first. |
| `direct_client.ts` | Calls the remote agent directly with `RemoteA2AAgent` + `Runner`. Needs no API key — the remote side owns the model call. |
| `consuming_agent.ts` | A local `root_agent` with a local `roll_agent` and the remote `prime_agent` as sub-agents. The model decides which one handles each request. |

## Setup

```bash
npm install
```

Create a `.env` file next to `package.json`:

```bash
GOOGLE_GENAI_API_KEY=your-api-key-here
```

Get a key at [Google AI Studio](https://aistudio.google.com/apikey).

## Run

Terminal 1 — the remote agent:

```bash
npm run serve
```

Terminal 2 — call it directly:

```bash
npm run direct
```

```text
user > Is 7 a prime number?
prime_agent > Yes, 7 is a prime number.
```

Terminal 2 — or let a local agent route to it:

```bash
npm run consume
```

```text
user > Roll a 6-sided die and tell me whether the result is prime.
root_agent calls transfer_to_agent({"agentName":"roll_agent"})
roll_agent calls roll_die({"sides":6})
roll_agent > I rolled a 6-sided die and got a 6.
roll_agent calls transfer_to_agent({"agentName":"prime_agent"})
prime_agent calls check_prime({"numbers":[6]})
prime_agent > 6 is not a prime number.
```

## Notes

- `remote_prime_agent.ts` passes `allowUnauthenticated: true`. That is for local
  development only: without it `toA2a()` refuses to mount.
- `agentCard` on `RemoteA2AAgent` is a **base URL**, not the URL of the card.
  Passing `http://localhost:8001/.well-known/agent-card.json` requests
  `/.well-known/.well-known/agent-card.json`, 404s, and crashes the process.
