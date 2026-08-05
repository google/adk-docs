# A2A Exposing Example (TypeScript)

This example exposes an ADK TypeScript agent over the A2A protocol so that other agents can
call it. It is the code used by
[A2A Quickstart (Exposing) for TypeScript](https://google.github.io/adk-docs/a2a/quickstart-exposing-typescript/).

## Files

- `remote_a2a/dice_agent/server.ts` — a dice-rolling `LlmAgent` exposed with `toA2a()` and
  served on `http://localhost:8001`. Uses `allowUnauthenticated: true`, which is for local
  development only.
- `remote_a2a/dice_agent/server-with-auth.ts` — the same agent behind a bearer-token
  `UserBuilder`, which is what you want anywhere other than localhost.

## Prerequisites

- Node.js 22 or later.
- Model credentials in a `.env` file in this directory — either a Google AI Studio key:

  ```bash
  GEMINI_API_KEY="YOUR_API_KEY"
  ```

  or a Google Cloud project with Vertex AI enabled and Application Default Credentials set up
  (`gcloud auth application-default login`):

  ```bash
  GOOGLE_GENAI_USE_VERTEXAI=true
  GOOGLE_CLOUD_PROJECT="your-project-id"
  GOOGLE_CLOUD_LOCATION="global"
  ```

## Run

```bash
npm install
npm run serve   # tsx remote_a2a/dice_agent/server.ts
```

Add `--env-file=.env` when running the script directly — ADK does not load `.env` on its own:

```bash
npx tsx --env-file=.env remote_a2a/dice_agent/server.ts
```

To run the authenticated variant instead, add the shared secret to the same `.env`
(`A2A_SHARED_TOKEN="s3cret-token"`) rather than passing it on the command line, where it would
be visible to `ps` and saved in your shell history:

```bash
npx tsx --env-file=.env remote_a2a/dice_agent/server-with-auth.ts
```

Then send a request with `-H 'Authorization: Bearer s3cret-token'`. Without the header, or with
the wrong token, you get JSON-RPC error `-32603` and HTTP 500.

## Verify

Fetch the auto-generated agent card:

```bash
curl -s http://localhost:8001/.well-known/agent-card.json | python3 -m json.tool
```

Then send a request over JSON-RPC:

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

A successful response is a task with `"state": "completed"` whose last artifact holds the
agent's answer, for example `"You rolled a 17."`.

## Typecheck

```bash
npm run typecheck
```
