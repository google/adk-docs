# Build a streaming agent with TypeScript

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-typescript">TypeScript v1.5.0</span>
</div>

By the end of this page you will have a web page at `http://localhost:3000` with
a text box and a **Send** button. You type a question, press Send, and the
agent's answer appears in the page a few words at a time *while the model is
still writing it* — not as one block of text after a long pause. You will build
an `LlmAgent`, an Express endpoint that forwards its events to the browser as
[Server-Sent Events](https://developer.mozilla.org/docs/Web/API/Server-sent_events),
and one static HTML file that reads them with `fetch`.

!!! warning "Streaming is off by default. This is the mistake everyone makes."

    `RunConfig.streamingMode` defaults to `StreamingMode.NONE`, and in that mode
    `runner.runAsync()` yields **exactly one event** — after the model has
    finished — containing the entire answer. Every example here passes
    `runConfig: {streamingMode: StreamingMode.SSE}`. Delete that line and the
    code still runs and still returns the right answer; it just stops streaming.

## The complete program {#complete-program}

The whole idea is two files. `agent.ts` builds the agent, which you will write
in [step 3](#step-3); the file below imports it, runs it in streaming mode, and
writes each chunk to standard output as it arrives. Everything specific to
streaming is here. You will save it as `stream-to-console.ts` in
[step 4](#step-4).

```typescript title="stream-to-console.ts"
--8<-- "examples/typescript/snippets/live/streaming/stream-to-console.ts:full"
```

Here is what is happening in this code:

1.  `runner.runAsync()` is an async generator, so you consume it with
    `for await`. There is no callback and no `EventEmitter`.
2.  `runConfig: {streamingMode: StreamingMode.SSE}` is what turns streaming on.
    Without it the loop body executes once.
3.  `event.errorCode` is checked first. A model failure — a bad API key, a model
    your project cannot access — arrives as an ordinary event with `errorCode`
    and `errorMessage` set. **`runAsync` does not throw**, so a loop that only
    reads text sees `undefined` and prints nothing at all.
4.  `textOf(event)` takes an `Event` and returns a `string`. It joins every part
    that has `text` and drops parts flagged `thought` (thinking models emit
    those) — so `parts[0]` is not assumed to be the answer. Events produced by
    tool calls have no text at all, which is why the loop skips empty results.
    It is imported, not redefined, because `server.ts` needs the same extraction
    in [step 5](#step-5).
5.  `event.partial` distinguishes a chunk from the end. When it is `true`, the
    text is a **delta** and you append it. On the last event ADK re-sends the
    **entire** accumulated answer with `partial: false`, so you *replace*
    `answer` rather than appending — appending there renders the answer twice.

## Use this page when {#when-to-use}

Use this page when you want an agent's text answer to appear progressively in a
UI you control. If you only want a chat window to poke at your agent during
development, run `npx adk web` instead — see the
[TypeScript quickstart](../../get-started/typescript.md).

Bidirectional live **audio and video** streaming is not available in the ADK
TypeScript SDK. `Runner` exposes no live entry point, and the agent-level live
path throws `Error: LlmAgent.runLiveFlow not implemented`. If you need live
audio today, see [Build a streaming agent with Python](streaming-python.md).

## Prerequisites {#prerequisites}

*   **Node.js 22 or later.** Check with `node --version`.
*   **Access to a Gemini model, by either route.** A
    [Google AI Studio API key](https://aistudio.google.com/app/apikey), or a
    Google Cloud project with the Vertex AI API enabled and the `gcloud` CLI
    installed. [Step 2](#step-2) sets up whichever one you have; nothing else on
    this page differs between them.

## 1. Create the project {#step-1}

```bash
mkdir adk-streaming && cd adk-streaming
mkdir public
npm init --yes
npm pkg set type="module"
```

Then install the dependencies:

=== "npm"

    ```bash
    npm install @google/adk@^1.5.0 express@^5.1.0
    npm install -D typescript@^5.9.2 tsx@^4.20.0 @types/node@^22.0.0 @types/express@^5.0.0
    ```

=== "pnpm"

    ```bash
    pnpm add @google/adk@^1.5.0 express@^5.1.0
    pnpm add -D typescript@^5.9.2 tsx@^4.20.0 @types/node@^22.0.0 @types/express@^5.0.0
    ```

=== "yarn"

    ```bash
    yarn add @google/adk@^1.5.0 express@^5.1.0
    yarn add -D typescript@^5.9.2 tsx@^4.20.0 @types/node@^22.0.0 @types/express@^5.0.0
    ```

`@google/adk` is the agent framework. `express` serves the HTTP endpoint and the
static HTML file — ADK ships no HTTP layer of its own, so this part is yours to
choose. `tsx` runs `.ts` files directly so there is no build step, and
`@types/node` and `@types/express` give you types for both.

The versions are pinned because the `package.json` below declares those same
ranges, and because `@types/node` should track the Node.js major you actually
run. Leave them off and npm installs today's `typescript` and `@types/node`
majors, which do not satisfy the file you are about to paste: `npm ls` then
reports `ELSPROBLEMS` on a project that has not even run yet.

Add the scripts and a TypeScript config. The `--env-file=.env` flag on the
`console` and `start` scripts is what loads the credentials you add in
[step 2](#step-2); without it, nothing reads the file.

```json title="package.json"
--8<-- "examples/typescript/snippets/live/streaming/package.json"
```

```json title="tsconfig.json"
--8<-- "examples/typescript/snippets/live/streaming/tsconfig.json"
```

The two settings that matter in `tsconfig.json` are `"module": "nodenext"` and
`"moduleResolution": "nodenext"`, paired with `"type": "module"` in
`package.json`. `@google/adk` is an ES module and these files use top-level
`await`. Set `"module": "commonjs"` instead and `tsc` reports
`error TS1378: Top-level 'await' expressions are only allowed when the 'module' option is set to …`.

## 2. Add your credentials {#step-2}

Pick the tab for the credentials you have. Each one is complete: create a file
named `.env` next to `package.json` containing exactly the lines shown, and
nothing else on this page changes.

=== "Google AI Studio API key"

    Create a key on the [API keys](https://aistudio.google.com/app/apikey) page,
    then put it in `.env`:

    ```bash title=".env"
    GEMINI_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
    ```

    Replace `PASTE_YOUR_ACTUAL_API_KEY_HERE` with your actual key. ADK reads
    `GEMINI_API_KEY` (or `GOOGLE_GENAI_API_KEY`); no other spelling works, and
    `GOOGLE_API_KEY` in particular is **not** read on this path.

=== "Google Cloud / Vertex AI"

    There is no API key on this path. Authenticate once:

    ```bash
    gcloud auth application-default login
    ```

    Then create `.env` with your own project id:

    ```bash title=".env"
    GOOGLE_GENAI_USE_VERTEXAI=TRUE
    GOOGLE_CLOUD_PROJECT=your-project-id
    GOOGLE_CLOUD_LOCATION=global
    ```

    `GOOGLE_GENAI_USE_VERTEXAI` takes priority: set it and `GEMINI_API_KEY` is
    ignored, even if it is still in the file. `GOOGLE_CLOUD_LOCATION=global`
    routes to wherever the model is served; a specific region such as
    `us-central1` works too, but only for models that region actually carries.
    For service accounts, Express Mode, and the other authentication options,
    see
    [Connect to Google Cloud and Agent Platform](../../get-started/google-cloud.md).

Add `.env` to your `.gitignore` before you commit anything. From here on the two
paths are identical — the log line ADK prints on every model call is what tells
you which one you are on, `backend: GEMINI_API` or `backend: VERTEX_AI`.

## 3. Define the agent {#step-3}

```typescript title="agent.ts"
--8<-- "examples/typescript/snippets/live/streaming/agent.ts:full"
```

Here is what is happening in this code:

1.  `explainerAgent` is an `LlmAgent`. Its `instruction` asks for three
    paragraphs purely so there is enough text to watch arrive; a one-word answer
    streams too fast to see.
2.  `InMemoryRunner` bundles a `Runner` with an in-memory session service, so
    there is nothing to configure for local development. See
    [Deploying this](#deploying) for what to change before production.
3.  `APP_NAME` is exported because the runner and every session lookup must use
    the same app name, and `server.ts` needs it too.
4.  `textOf()` lives here, rather than in each consumer, because both
    `stream-to-console.ts` and `server.ts` need exactly the same text
    extraction. `Event` is brought in with `import type`, which keeps it out of
    the emitted JavaScript.

## 4. Stream to your terminal {#step-4}

Before wiring up HTTP, confirm that chunks really are arriving. Save
[the complete program](#complete-program) from the top of this page as
`stream-to-console.ts`, next to `agent.ts`, then run:

```bash
npm run console
```

There is a pause of a second or two while the model starts, and then the answer
types itself out in a handful of visible bursts — a few hundred characters at a
time, not one block — followed by a line like `--- 1273 characters ---`. Watch
for the *bursts*, not the clock: how long it takes depends on the prompt, the
model and your network, and a short answer can finish before you register it.
If instead the terminal sits silent and then prints everything at once,
`streamingMode` is missing — see [Troubleshooting](#troubleshooting).

## 5. Serve the stream over HTTP {#step-5}

```typescript title="server.ts"
--8<-- "examples/typescript/snippets/live/streaming/server.ts:full"
```

Here is what is happening in this code:

1.  `req.body` is `any`, so it is annotated on the way out —
    `as {userId: string; sessionId: string; message: string}` — and the three
    destructured names are typed from there. `APP_NAME`, `runner` and `textOf`
    all come from `agent.ts`; the server adds HTTP and nothing else.
2.  `runner.sessionService.getSession()` runs first because `runAsync` requires a
    session that already exists. If there is none, `createSession()` makes one
    with the `sessionId` the browser sent, so follow-up questions keep their
    history.
3.  The three SSE headers (`Content-Type: text/event-stream`,
    `Cache-Control: no-cache`, `Connection: keep-alive`) tell the browser this is
    a stream. `X-Accel-Buffering: no` stops nginx and similar proxies from
    buffering it back into one response.
4.  **`res.flushHeaders()` is mandatory.** Without it Node holds the headers
    until the first flush and the browser receives nothing until the run ends —
    which looks exactly like streaming being broken.
5.  `res.on('close')` aborts the `AbortController` whose `signal` was passed to
    `runAsync` as `abortSignal`. Close the browser tab and generation stops;
    leave this out and an abandoned tab keeps burning tokens.
6.  `send()` writes one SSE frame: the literal prefix `data: `, a JSON payload,
    and a **blank line** (`\n\n`) as the frame terminator. The blank line is what
    the client splits on.
7.  Only `event.partial` deltas are forwarded. The final aggregated event is
    deliberately dropped, because it repeats the entire answer — forwarding it
    would print the answer twice in the browser. `send({done: true})` marks the
    end instead.

## 6. Build the browser client {#step-6}

```html title="public/index.html"
--8<-- "examples/typescript/snippets/live/streaming/public/index.html"
```

Here is what is happening in this code:

1.  The request uses `fetch` with `response.body.getReader()`, **not
    `EventSource`**. `EventSource` can only issue `GET` requests and this
    endpoint needs a POST body.
2.  `sessionId` is generated once per page load with `crypto.randomUUID()` and
    sent with every message, so the agent remembers the conversation.
3.  `decoder.decode(value, {stream: true})` turns each `Uint8Array` into text
    without cutting multi-byte characters in half at a chunk boundary.
4.  `buffer.split('\n\n')` splits the accumulated text into frames, and
    `frames.pop()` puts the last piece **back into `buffer`**. A single `data:`
    frame can be split across two network reads, and this is what stops you from
    calling `JSON.parse` on half a frame.
5.  `answer.textContent += payload.delta` is a plain append, which is correct
    *only because* `server.ts` already dropped the duplicated final event. If you
    ever forward raw ADK events to the browser, the browser has to do the
    append-on-`partial`, replace-on-final dance from
    [the complete program](#complete-program) instead.

## 7. Run it {#step-7}

```bash
npm start
```

If port 3000 is already taken (`Error: listen EADDRINUSE`), pick another —
`server.ts` reads `PORT`, so `PORT=3100 npm start` serves on
<http://localhost:3100> instead.

Open <http://localhost:3000>. You should see the heading **Ask the agent**, a
text box pre-filled with `Why is the sky blue?`, and a **Send** button. Press
Send. The button greys out, and a second or two later text starts appearing
below the form and keeps growing in bursts until the button becomes clickable
again. Ask something else and the agent will remember what you asked before.

That is a streaming agent UI. The rest of this page is what to do when it
misbehaves.

## What the events actually look like {#events}

`runAsync` yields `Event` objects. For text streaming these are the fields that
matter:

| Field | Type | What it tells you |
| :--- | :--- | :--- |
| `content.parts[].text` | `string \| undefined` | The text. Absent on tool-call and tool-response events. |
| `content.parts[].thought` | `boolean \| undefined` | `true` marks a reasoning part from a thinking model, not the answer. Filter these out. |
| `partial` | `true \| false \| undefined` | `true` = incremental chunk, text is a delta. Otherwise the text is the complete answer so far. |
| `errorCode` / `errorMessage` | `string \| undefined` | Set when the model call failed. Nothing is thrown. |
| `author` | `string \| undefined` | The name of the agent that produced the event, or `'user'`. |

Two properties of `partial` catch people out:

*   It is **tri-state**. It can be `undefined` — on non-streaming runs and on
    tool-response events. Test it for truthiness (`if (event.partial)`), never
    `event.partial === false`.
*   `partial: false` does **not** mean "the run is over". A tool-call event
    carries `partial: false` in the middle of a run. If you need a genuine
    end-of-turn signal, import `isFinalResponse` from `@google/adk` and call
    `isFinalResponse(event)`.

Do not branch on `turnComplete`, and do not depend on where chunk boundaries
fall — they are an implementation detail of the aggregator and shift between
releases.

`StreamingMode.BIDI` exists in the enum but is reserved. Passing it produces
non-streaming behaviour with no error and no warning; use `StreamingMode.SSE`.

## Troubleshooting {#troubleshooting}

**The whole answer appears at once after a long pause.**
`runConfig: {streamingMode: StreamingMode.SSE}` is missing, or is set to
`StreamingMode.NONE` or `StreamingMode.BIDI`. To confirm, look at the log line
ADK prints on every model call: it ends with `stream: false` when streaming is
off and `stream: true` when it is on.

```
INFO: [ADK] 2026-01-01T00:00:00.000Z Sending out request, model: gemini-2.5-flash, backend: GEMINI_API, stream: false
```

**The answer appears twice, end to end.**
You are appending the text of every event. The last event carries the full
answer with `partial: false`, so `text += chunk` over all events yields exactly
double. Append only when `event.partial` is truthy, and replace on the final
event — or drop the final event server-side as `server.ts` does.

**Nothing renders and there is no error anywhere.**
Model failures are delivered as events, not exceptions: `runAsync` returns
normally and your process exits `0`. Check `event.errorCode` inside the loop. A
bad key surfaces like this:

```
[400] {
  "error": {
    "code": 400,
    "message": "API key not valid. Please pass a valid API key.",
    "status": "INVALID_ARGUMENT",
```

**`Error: API key must be provided via constructor or GOOGLE_GENAI_API_KEY or GEMINI_API_KEY environment variable.`**
No key reached the process. Either `.env` is missing, or it is spelled
`GOOGLE_API_KEY` (which ADK does not read for the Gemini API), or you started
the process without `--env-file=.env`.

**The browser shows nothing until the answer is complete, but `npm run console` streams fine.**
`res.flushHeaders()` is missing from the route handler. Node buffers the
response until the first flush, so the whole stream lands in one piece at the
end.

**A `SyntaxError` from `JSON.parse` in the browser console, and a chunk of text goes missing.**
The client parsed a frame that a network read cut in half. The exact message
depends on where the split landed — one read gives you `data: {"delta"` and the
next gives you `:"hello world"}`, so you get something like
`SyntaxError: Expected ':' after property name in JSON at position 8`, and the
second half is silently dropped because it does not start with `data: `. Split
the accumulated buffer on `'\n\n'`, `pop()` the trailing fragment, and keep it
for the next `reader.read()` — see [step 6](#step-6). This is rare on
`localhost` and common the moment there is a real network or a proxy in the
path, so do not skip it because it worked in development.

**Blank bubbles appear in the UI when the agent uses a tool.**
Tool-call and tool-response events have no text. Skip any event whose extracted
text is empty, as `textOf()` does.

**`ERROR: Top-level await is currently not supported with the "cjs" output format`.**
`package.json` is missing `"type": "module"`. `@google/adk` is an ES module and
these files use top-level `await`; the ESM settings from [step 1](#step-1) —
`"type": "module"` in `package.json` and `"module": "nodenext"` in
`tsconfig.json` — are both required.

## Deploying this {#deploying}

Two things in the code above are development-only:

*   `InMemoryRunner` keeps sessions in process memory. They vanish on restart and
    are invisible to a second instance. Use a persistent `SessionService` in
    production.
*   `@google/adk` requires a Node.js runtime. It will not run on edge runtimes;
    on Next.js that means `export const runtime = 'nodejs'` in the route handler.

## Next steps {#next-steps}

*   [Give your agent tools so it can call external APIs](../../tools-custom/function-tools.md)
    — tool calls interleave extra events into the stream you just built.
*   [Stop a run in flight when the user navigates away](../../runtime/cancel.md)
    — the `AbortSignal` pattern `server.ts` uses, in depth.
*   [Keep conversation history across restarts](../../sessions/session/index.md)
    — replacing `InMemoryRunner`'s session storage.
*   [Change how much the model streams and how it responds](../configuration.md)
    — the rest of `RunConfig`.
