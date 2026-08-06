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
3.  `TurnText` tracks what has already been printed, and `turn.unshown(event)`
    returns only what has not — `''` when there is nothing new. It is imported,
    not redefined, because `server.ts` needs the same bookkeeping in
    [step 5](#step-5). It is built on `textOf()`, which joins every part that
    has `text` and drops parts flagged `thought` (thinking models emit those) —
    so `parts[0]` is not assumed to be the answer. Tool-call and tool-response
    events carry no text at all, which is why the loop skips empty results.
4.  That bookkeeping exists because ADK sends the same text in two shapes. Each
    chunk arrives with `partial: true` and is a **delta**, and then ADK re-sends
    that whole block in one event with `partial: false`. Appending both renders
    the answer twice, so `unshown()` appends deltas and returns only the tail of
    the `partial: false` event — usually nothing. *Usually*, not always: when
    one model chunk carries text **and** a tool call, ADK splits it into a
    consolidated text event followed by the tool-call event, and that text was
    never sent as a delta. Ignoring `partial: false` events outright, rather
    than de-duplicating them, silently drops it the day your agent gets tools.
5.  `event.errorCode` is checked on every event, and after the write, because
    the event that reports a truncated run carries the last of its text too. A
    model failure — a bad API key, a model your project cannot access — arrives
    as an ordinary event with `errorCode` set. **Model failures do not throw**,
    so a loop that only reads text sees `undefined` and prints nothing at all.
    (`runAsync` itself does throw for other things; see
    [What the events actually look like](#events).) An `errorMessage` is not
    guaranteed to come with the code, which is why `detail` appends it only when
    it is there: print it unconditionally and a run that hits the token limit
    reports `[MAX_TOKENS] undefined`.

## Use this page when {#when-to-use}

Use this page when you want an agent's text answer to appear progressively in a
UI you control. If you only want a chat window to poke at your agent during
development, install the dev tools — `npm install -D @google/adk-devtools` —
and run `npx adk web` instead; see the
[TypeScript quickstart](../../get-started/typescript.md). The install is not
optional and the project on this page does not include it: the `adk` command
comes from `@google/adk-devtools`, and `npx adk` in a project without it fails
with `npm ERR! could not determine executable to run` — or fetches an unrelated
`adk` package from the public registry.

Bidirectional live **audio and video** streaming is not available in the ADK
TypeScript SDK. `Runner` exposes no live entry point, and the agent-level live
path throws `Error: LlmAgent.runLiveFlow not implemented`. If you need live
audio today, see [Build a streaming agent with Python](streaming-python.md).

## Prerequisites {#prerequisites}

*   **Node.js 22 or later.** Check with `node --version`. That is the floor this
    page was written and tested against, not an enforced one — adk-js declares
    no `engines` field, so npm will not stop you on an older runtime.
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
`package.json`. That is not about `@google/adk`, which ships a CommonJS build
alongside its ES module one and imports fine either way. It is about
`stream-to-console.ts`, which `await`s at the top level — something only an ES
module can do. Set `"module": "commonjs"` instead and `tsc` reports
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
4.  `textOf()` and `TurnText` live here, rather than in each consumer, because
    `stream-to-console.ts` and `server.ts` need exactly the same text extraction
    and exactly the same "have I shown this already?" bookkeeping. `TurnText`
    holds per-run state, so each consumer makes its own — one per `runAsync`
    loop, which for the server means one per request. `Event` is brought in with
    `import type`, which keeps it out of the emitted JavaScript.

## 4. Stream to your terminal {#step-4}

Before wiring up HTTP, confirm that chunks really are arriving. Save
[the complete program](#complete-program) from the top of this page as
`stream-to-console.ts`, next to `agent.ts`, then run:

```bash
npm run console
```

**Expect several seconds of nothing first.** Across the runs behind this page the
first characters appeared roughly 6 to 11 seconds after pressing Enter, and most
of that is not the model: `tsx` has to compile, `@google/adk` has to load and
credentials have to be resolved before the request is even sent — about four
seconds — and only then does the model spend a further one and a half to seven
seconds on its first token. Do not conclude it is broken and kill it. The one
log line ADK prints, `Sending out request, model: …`, is your marker: everything
before it is startup, everything after it is the model.

Then the answer types itself out in a handful of visible bursts — a few hundred
characters at a time, not one block — followed by a line like
`--- 1273 characters ---`. Watch for the *bursts*, not the clock: a short answer
can finish before you register it. If instead the terminal sits silent and then
prints everything at once, `streamingMode` is missing — see
[Troubleshooting](#troubleshooting).

## 5. Serve the stream over HTTP {#step-5}

```typescript title="server.ts"
--8<-- "examples/typescript/snippets/live/streaming/server.ts:full"
```

Here is what is happening in this code:

1.  `req.body` is `any`, so it is annotated on the way out —
    `as {userId: string; sessionId: string; message: string}` — and the three
    destructured names are typed from there. `APP_NAME`, `runner` and `TurnText`
    all come from `agent.ts`; the server adds HTTP and nothing else.
2.  `runner.sessionService.getSession()` runs first because `runAsync` requires a
    session that already exists. If there is none, `createSession()` makes one
    with the `sessionId` the browser sent, so follow-up questions keep their
    history.
3.  The three SSE headers (`Content-Type: text/event-stream`,
    `Cache-Control: no-cache`, `Connection: keep-alive`) tell the browser this is
    a stream. `X-Accel-Buffering: no` stops nginx and similar proxies from
    buffering it back into one response.
4.  `res.flushHeaders()` sends the headers *now*, before the first token exists.
    Without it Node holds them until the first `res.write()`, so the browser's
    `fetch` promise does not resolve — and `response.body.getReader()` cannot
    start reading — until the model has already produced something. Measured on
    this example: headers within a few tens of milliseconds with
    `flushHeaders()`, and 2.3–4.0 s without it. It does not change how the body
    arrives; the deltas stream in five to seven pieces either way.
5.  `res.on('close')` aborts the `AbortController` whose `signal` was passed to
    `runAsync` as `abortSignal`. Close the browser tab and generation stops;
    leave this out and an abandoned tab keeps burning tokens.
6.  `send()` writes one SSE frame: the literal prefix `data: `, a JSON payload,
    and a **blank line** (`\n\n`) as the frame terminator. The blank line is what
    the client splits on.
7.  `turn.unshown(event)` picks what to forward, so the browser is sent each
    piece of the answer exactly once: the delta of a `partial: true` event, and
    of a `partial: false` event only the part that was never streamed. For the
    tool-free agent here that part comes out empty. For an agent with tools it
    is the sentence the model wrote in the same chunk as its tool call — text
    that a server forwarding only `event.partial` never sends at all.
    `send({done: true})` marks the end.
8.  The `'error'` handler on the server is **not optional**. Express 5 registers
    the callback you pass to `app.listen(port, cb)` as an `'error'` listener as
    well, so the one-line version everyone writes —
    `app.listen(port, () => console.log('Open …'))` — greets you with
    `Open http://localhost:3000` and exits `0` when the port is busy. Nothing is
    listening and nothing said so. Binding `'listening'` and `'error'`
    separately means the success line only prints on success, and a failure to
    bind prints why and exits non-zero.

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
    *only because* `server.ts` never sends the same text twice. If you ever
    forward raw ADK events to the browser instead, the browser has to do the
    `TurnText` bookkeeping from [the complete program](#complete-program)
    itself.

## 7. Run it {#step-7}

```bash
npm start
```

If port 3000 is already taken, nothing starts and you get this on stderr, with
exit code `1`:

```
Port 3000 is already in use. Free it, or run PORT=3100 npm start.
```

`server.ts` reads `PORT`, so `PORT=3100 npm start` serves on
<http://localhost:3100> instead.

Open <http://localhost:3000>. You should see the heading **Ask the agent**, a
text box pre-filled with `Why is the sky blue?`, and a **Send** button. Press
Send. The button greys out — and then **nothing happens for several seconds**.
That wait was 1.3 to 4.0 seconds on the runs behind this page, and longer is
normal on a slower link; it is the model's time to its first token and there is
nothing to see until it passes. Then text starts appearing below the form and
keeps growing in bursts until the button becomes clickable again. Ask something
else and the agent will remember what you asked before.

That is a streaming agent UI. The rest of this page is what to do when it
misbehaves.

## What the events actually look like {#events}

`runAsync` yields `Event` objects. For text streaming these are the fields that
matter:

| Field | Type | What it tells you |
| :--- | :--- | :--- |
| `content.parts[].text` | `string \| undefined` | The text. Absent on tool-call and tool-response events. |
| `content.parts[].thought` | `boolean \| undefined` | `true` marks a reasoning part from a thinking model, not the answer. Filter these out. |
| `partial` | `true \| false \| undefined` | `true` = incremental chunk, text is a delta. Otherwise the text is the whole block since the previous `partial: false` event — for a tool-free agent, the complete answer. |
| `errorCode` / `errorMessage` | `string \| undefined` | `errorCode` is set when the model call failed **and** whenever the model stopped for any reason other than `STOP` — `MAX_TOKENS`, `SAFETY`. An `errorMessage` is not guaranteed with it, so print the code alone when it is missing: `[MAX_TOKENS]`, not `[MAX_TOKENS] undefined`. Neither case throws. |
| `author` | `string \| undefined` | The name of the agent that produced the event, or `'user'`. |

Two properties of `partial` catch people out:

*   It is **tri-state**. It can be `undefined` — on non-streaming runs and on
    tool-response events. Test it for truthiness (`if (event.partial)`), never
    `event.partial === false`.
*   `partial: false` does **not** mean "the run is over". A tool-call event
    carries `partial: false` in the middle of a run. If you need a genuine
    end-of-turn signal, import `isFinalResponse` from `@google/adk` and call
    `isFinalResponse(event)`.

The events are the only thing `runAsync` reports a *model* failure through, and
that is what makes them easy to ignore. It is not a blanket promise that nothing
throws: `runAsync` throws `Error: Session not found: <id>` if you pass a session
id that does not exist, and it re-throws anything a model rejected with that is
not an `Error`. Both surface on the `for await`. `server.ts` wraps its loop in a
`try` for exactly that reason — a thrown error there would kill the process
instead of the request; `stream-to-console.ts` lets it crash, which is what you
want in a one-shot script.

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
You are appending the text of every event. The last event repeats the whole
block with `partial: false`, so `text += chunk` over all events yields exactly
double — measured at 2.000× on the runs behind this page. Track what you have
already shown and take only the new tail from a `partial: false` event, as
`TurnText` does.

**Text disappears as soon as the agent has a tool.**
The opposite mistake, and the tempting fix for the one above: skipping every
`partial: false` event. When a model chunk carries text *and* a tool call — "Let
me look that up." followed by the call — that text is never sent as a delta, so
the `partial: false` event is the only event carrying it and skipping it drops
it. A tool-free agent never shows this, which is why it survives review. Use
`TurnText` rather than a `partial` check and both cases are right.

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

**The browser shows nothing for several seconds after you press Send.**
Usually this is just the model's time to first token — 1.3 to 4.0 seconds here —
and not a bug. Confirm with `npm run console`: if the terminal pauses too, the
stream is fine.

If it is longer than that, and `fetch` in the browser does not resolve at all
until the first text appears, `res.flushHeaders()` is missing from the route
handler. Node then holds the response headers until the first `res.write()`, so
the client cannot begin reading until the model has produced something. The
deltas still arrive in pieces once they start, so this does not look like
streaming being off — it looks like the endpoint is slow to respond.

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
text is empty — `textOf()` returns `''` for them, and so does
`TurnText.unshown()`.

**`ERROR: Top-level await is currently not supported with the "cjs" output format`.**
`package.json` is missing `"type": "module"`, so `tsx` compiles as CommonJS —
and `stream-to-console.ts` `await`s at the top level, twice, which CommonJS has
no equivalent for. Note which file the error names: yours, not the import.
`@google/adk` is dual-published, its `exports` map resolving `require` to a
CommonJS build, and it loads fine from CommonJS — which is why `npm start`
survives this misconfiguration and only `npm run console` dies. Restore the ESM
settings from [step 1](#step-1): `"type": "module"` in `package.json` and
`"module": "nodenext"` in `tsconfig.json`.

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
