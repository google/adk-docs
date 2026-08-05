# TypeScript Quickstart for ADK

In this quickstart you build an agent that answers a question by calling a
TypeScript function you wrote, and then talk to it from your terminal. Four
steps, one file.

**Prerequisites**

*   **Node.js 22 or later.** Check with `node --version`. This guide was
    verified end to end on Node.js v22.22.2 with npm 9.2.0.
*   **npm, pnpm, or yarn.** Every command below is given for all three.
*   **A Gemini API key.** Create one in Google AI Studio on the
    [API Keys](https://aistudio.google.com/app/apikey) page. If you would rather
    authenticate with Google Cloud, [step 3](#3-set-your-credentials) covers
    that too.

## 1. Write the agent

Create a `my-agent` directory, and inside it an `agent.ts` file containing a
[Function Tool](/tools-custom/function-tools/) named `getCurrentTime` and an
agent that uses it:

```typescript title="my-agent/agent.ts"
import {FunctionTool, LlmAgent} from '@google/adk';
import {z} from 'zod';

/* Mock tool implementation */
const getCurrentTime = new FunctionTool({
  name: 'getCurrentTime',
  description: 'Returns the current time in a specified city.',
  parameters: z.object({
    city: z.string().describe("The name of the city for which to retrieve the current time."),
  }),
  execute: ({city}) => {
    return {status: 'success', report: `The current time in ${city} is 10:30 AM`};
  },
});

export const rootAgent = new LlmAgent({
  name: 'helloTimeAgent',
  model: 'gemini-flash-latest',
  description: 'Tells the current time in a specified city.',
  instruction: `You are a helpful assistant that tells the current time in a city.
                Use the 'getCurrentTime' tool for this purpose.`,
  tools: [getCurrentTime],
});
```

Let's take a look at what is happening in this code:

1.  `name: 'getCurrentTime'` is the identifier the model uses to call the tool,
    and `description` is how it decides *when* to call it. The `instruction`
    on the agent names the same string, `getCurrentTime`. If those two strings
    disagree, the model asks for a tool that does not exist and your function
    never runs.
2.  `parameters` is a Zod schema, and it is the tool's whole input contract:
    ADK turns it into the function declaration sent to the model, validates the
    model's arguments against it, and infers the type of `execute`'s argument
    from it. In `execute: ({city}) =>`, `city` is already typed `string` — you
    never declare that type twice.
3.  `execute` returns a plain object. ADK serializes it and hands it back to the
    model, which turns it into the sentence you see.
4.  `LlmAgent` binds the three things an agent needs: a `model`, an
    `instruction`, and its `tools`.
5.  The export **must** be named `rootAgent`. Both `adk run` and `adk web` look
    for that exact export and fail without it.

## 2. Install dependencies

Move into the project directory and install:

=== "npm"

    ```console
    cd my-agent/
    npm init --yes
    npm pkg set type="module" main="agent.ts"
    npm install @google/adk zod
    npm install -D @google/adk-devtools
    ```

=== "pnpm"

    ```console
    cd my-agent/
    pnpm init
    pnpm pkg set type="module" main="agent.ts"
    pnpm add @google/adk zod
    pnpm add -D @google/adk-devtools
    pnpm approve-builds --all
    ```

    Five packages ship install scripts, which pnpm blocks by default. pnpm
    prints the list after each install; once both are done it reads:

    ```console
    [ERR_PNPM_IGNORED_BUILDS] Ignored build scripts: @google/genai@1.52.0, @google/genai@2.15.0, esbuild@0.25.12, protobufjs@7.6.5, sqlite3@5.1.7
    ```

    `@google/genai` is listed twice because `@google/adk` and
    `@google/adk-devtools` pull different majors of it, and `esbuild` is missing
    from the earlier list — the one after `pnpm add @google/adk zod` — because it
    arrives with the devtools. Until you approve them, every `pnpm exec` fails
    its dependency check with that same message before running anything.

=== "yarn"

    ```console
    cd my-agent/
    yarn init -2
    yarn config set nodeLinker node-modules
    npm pkg set type="module" main="agent.ts"
    yarn add @google/adk zod
    yarn add -D @google/adk-devtools
    ```

    Yarn's default Plug'n'Play linker cannot load `@google/adk-devtools`, so set
    `nodeLinker` to `node-modules` before installing. See
    [Troubleshooting](#troubleshooting) for the error you get if you skip it.

Three packages, and each one earns its place:

*   `@google/adk` is the agent framework — `LlmAgent`, `FunctionTool`, and the
    Gemini model layer.
*   `zod` is imported directly by your `agent.ts`, so it has to be a dependency
    of *your* project. npm happens to hoist it out of `@google/adk`, but pnpm
    and yarn will not, and your agent will fail to build.
*   `@google/adk-devtools` provides the `adk` command used in step 4. It is a
    dev dependency; your deployed agent does not need it.

**You should see:** a `node_modules/` directory, and `npx adk --version`
(`pnpm exec adk --version`, `yarn adk --version`) printing `1.5.0`.

## 3. Set your credentials

ADK for TypeScript reads its credentials from the process environment, and from
a `.env` file in the directory you run the command from — which is `my-agent/`,
because that is where step 4 tells you to run. Create `my-agent/.env`:

=== "Gemini API key"

    ```console title="my-agent/.env"
    GOOGLE_GENAI_API_KEY="PASTE_YOUR_API_KEY_HERE"
    ```

    Replace `PASTE_YOUR_API_KEY_HERE` with the key you created in
    [Google AI Studio](https://aistudio.google.com/app/apikey). `GEMINI_API_KEY`
    is accepted as an alias for exactly the same purpose; pick one.

=== "Google Cloud Agent Platform"

    Authenticate your workstation with Application Default Credentials first:

    ```console
    gcloud auth application-default login
    ```

    Then create the `.env` file:

    ```console title="my-agent/.env"
    GOOGLE_GENAI_USE_VERTEXAI=TRUE
    GOOGLE_CLOUD_PROJECT=your-project-id
    GOOGLE_CLOUD_LOCATION=global
    ```

    Use `GOOGLE_GENAI_USE_VERTEXAI`. ADK for TypeScript does not read
    `GOOGLE_GENAI_USE_ENTERPRISE`; setting only that one leaves the agent
    looking for an API key it will not find. A regional
    `GOOGLE_CLOUD_LOCATION` such as `us-central1` also needs a versioned model
    string — change `model` to `gemini-2.5-flash`, because
    `gemini-flash-latest` does not resolve on regional endpoints.

!!! warning "Your shell wins over `.env`"

    `.env` is loaded without overriding, so a variable already exported in your
    shell keeps its value and the line in `.env` is ignored. This matters most
    on the Google Cloud path: many Cloud workstations already export
    `GOOGLE_CLOUD_PROJECT`, so the quickstart can succeed against *that* project
    while the `.env` you just wrote does nothing — and then fail for the next
    person who copies your file. Before you run, check what is already set:

    ```console
    env | grep -E '^(GOOGLE_|GEMINI_)'
    ```

    Anything printed there overrides `.env`. `unset` it, or set the value you
    actually want in the shell rather than in the file.

!!! warning "`GOOGLE_API_KEY` is not one of the names"

    On the Gemini API path, ADK for TypeScript reads `GOOGLE_GENAI_API_KEY` or
    `GEMINI_API_KEY` and nothing else. Setting `GOOGLE_API_KEY` fails with
    `Error: API key must be provided via constructor or GOOGLE_GENAI_API_KEY or
    GEMINI_API_KEY environment variable.` Other pages in these docs show
    `GOOGLE_API_KEY`; on this path it does not work.

Add `.env` to your `.gitignore` before you commit anything.

??? tip "Using other AI models with ADK"
    ADK supports the use of many generative AI models. For more
    information on configuring other models in ADK agents, see
    [Models & Authentication](/agents/models).

## 4. Run your agent

`@google/adk-devtools` gives you two ways to talk to the agent: an interactive
terminal session with `adk run`, and a browser chat UI with `adk web`.

### Run with the command-line interface

Run this from `my-agent/`, the directory that has `node_modules/` in it:

=== "npm"

    ```console
    npx adk run agent.ts
    ```

=== "pnpm"

    ```console
    pnpm exec adk run agent.ts
    ```

=== "yarn"

    ```console
    yarn adk run agent.ts
    ```

Type a question at the `[user]:` prompt and press Enter. A working session looks
like this:

```console title="Expected output"
(node:4048641) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
(Use `node --trace-deprecation ...` to show where the warning was created)
Running agent helloTimeAgent, type exit to exit.
[user]: What time is it in Paris?
INFO: [ADK] 2026-08-05T17:41:51.838Z Sending out request, model: gemini-flash-latest, backend: GEMINI_API, stream: false
INFO: [ADK] 2026-08-05T17:41:52.665Z Sending out request, model: gemini-flash-latest, backend: GEMINI_API, stream: false
[helloTimeAgent]: The current time in Paris is 10:30 AM
[user]: exit
```

Do not compare that character by character. The two `punycode` lines come from
Node, not from ADK — they precede *every* `adk` command on Node 22, the process
id in them changes each run, and more Node warnings may join them. The
timestamps are yours, and the model rephrases the last line freely.

**You should see** two `INFO` lines and then a `[helloTimeAgent]:` line carrying
the answer. Two requests is the tool call working: the first asks the model what
to do, the model asks for `getCurrentTime`, and the second sends your function's
result back for the model to phrase. On the Google Cloud path the same run
prints `backend: VERTEX_AI` instead of `backend: GEMINI_API`.

**If it fails you will not get an error.** ADK for TypeScript 1.5.0 prints one
`INFO` line, returns you to the `[user]:` prompt with no answer, and exits with
status `0`. The silence means the model request was rejected and ADK discarded
the reason. It is *not* specific to a bad key: an unusable API key, a project
your credentials cannot reach, and a model name that does not exist in your
region are all indistinguishable at the terminal. See
[Troubleshooting](#troubleshooting) for a command that prints the real error.

### Run with the web interface

```console
npx adk web
```

This starts a server on `http://localhost:8000`; pass `--port 8001` (or `-p`) to
use a different one. Open it and you should see a dark chat page titled
**Agent Development Kit**, with an app selector in the top left already showing
`agent` — the name comes from your `agent.ts` filename, not from
`rootAgent.name`. Type into **Type a message...** at the bottom. The event list
shows your message, then a `getCurrentTime("Paris")` call, then the tool's
result, then the answer.

![adk-web-dev-ui-chat.png](/assets/adk-web-dev-ui-chat.png)

!!! warning "Caution: ADK Web for development only"

    ADK Web is ***not meant for use in production deployments***. You should
    use ADK Web for development and debugging purposes only.

## Troubleshooting

**One `INFO` line, no answer, and exit code `0`.**

The model request was rejected and ADK discarded the reason, so the terminal
shows you nothing. At least three different causes produce this identical
silence, and you cannot tell them apart from the output:

*   an API key that the Gemini API rejects, or one whose project has the API
    disabled;
*   a `GOOGLE_CLOUD_PROJECT` your credentials are not authorized to use;
*   a `model` string that does not exist at your `GOOGLE_CLOUD_LOCATION` —
    notably `gemini-flash-latest`, which resolves on `global` but **not** on a
    regional endpoint such as `us-central1`.

Send the same request yourself to see the error ADK hid. On the Gemini API path:

```console
curl -s -X POST -H 'Content-Type: application/json' \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key=$GOOGLE_GENAI_API_KEY" \
  -d '{"contents":[{"role":"user","parts":[{"text":"hi"}]}]}'
```

On the Google Cloud path (use `LOCATION-aiplatform.googleapis.com` for a
regional `GOOGLE_CLOUD_LOCATION`):

```console
curl -s -X POST -H "Authorization: Bearer $(gcloud auth application-default print-access-token)" \
  -H 'Content-Type: application/json' \
  "https://aiplatform.googleapis.com/v1/projects/$GOOGLE_CLOUD_PROJECT/locations/$GOOGLE_CLOUD_LOCATION/publishers/google/models/gemini-flash-latest:generateContent" \
  -d '{"contents":[{"role":"user","parts":[{"text":"hi"}]}]}'
```

You get back the message ADK swallowed — `API key not valid. Please pass a valid
API key.`, `Permission denied on resource project <id>.`, or ``Publisher model
`...` was not found or your project does not have access to it``, which each
point at one of the three causes above. To check whether your credential is
being read at all, temporarily remove it: with nothing set, the run fails
loudly with `API key must be provided` instead of going quiet.

**`Error: API key must be provided via constructor or GOOGLE_GENAI_API_KEY or GEMINI_API_KEY environment variable.`**

No credential was found under a name ADK reads. You set `GOOGLE_API_KEY`, or
you set `GOOGLE_GENAI_USE_ENTERPRISE` instead of `GOOGLE_GENAI_USE_VERTEXAI`,
or your `.env` is not in the directory you ran the command from.

**`Error: VertexAI project must be provided via constructor or GOOGLE_CLOUD_PROJECT environment variable.`**

`GOOGLE_GENAI_USE_VERTEXAI` is set but `GOOGLE_CLOUD_PROJECT` is missing.

**`Error: VertexAI location must be provided via constructor or GOOGLE_CLOUD_LOCATION environment variable.`**

The same, for `GOOGLE_CLOUD_LOCATION`. Both variables are required on the Google
Cloud path and each one has its own error; setting only the project gets you
this one. Use `global` unless you need a specific region.

**`npm ERR! could not determine executable to run`**

`npx adk` did not find the local `adk` binary and reached for a package named
`adk` on the public registry — an unrelated third-party package that has nothing
to do with ADK. Run the command from the directory that contains
`node_modules/`, or invoke the binary directly with
`./node_modules/.bin/adk run agent.ts`.

**`✘ [ERROR] Could not resolve "zod"`**

`zod` is not a dependency of your project. Run `npm install zod` (or the pnpm
or yarn equivalent). npm's flat `node_modules` can mask this; pnpm and yarn
will not.

**`Error: @google/adk-devtools tried to access @opentelemetry/api, but it isn't declared in its dependencies`**

You are on Yarn's Plug'n'Play linker. Run `yarn config set nodeLinker
node-modules` and reinstall.

**`[ERR_PNPM_IGNORED_BUILDS] Ignored build scripts: @google/genai@1.52.0, @google/genai@2.15.0, esbuild@0.25.12, protobufjs@7.6.5, sqlite3@5.1.7`**

pnpm blocked those install scripts, and that makes `pnpm exec` fail its
dependency check before it runs anything. Run `pnpm approve-builds --all` once.
The exact versions move; the set does not.

**`[ADK CLI] Error starting web server: Port 8000 is already in use`**

Something already holds port 8000 — often an `adk web` you left running in
another terminal. Either serve on another port:

```console
npx adk web --port 8001
```

or find and stop what is holding 8000 first:

```console
lsof -ti :8000        # prints the process id
kill $(lsof -ti :8000)
```

`adk web` does not fall back to a free port on its own; it prints that line and
exits.

**`TypeError [ERR_UNKNOWN_FILE_EXTENSION]: Unknown file extension ".ts"`**

You ran `node agent.ts`. Node does not execute TypeScript here, and `agent.ts`
only exports an agent — it has no entry point. Use `adk run agent.ts`, which
compiles the file before loading it.

**`AgentFileLoadingError`** ending in **`does not exists`**

Wrong path or wrong extension. The argument to `adk run` is the path to your
TypeScript source, `agent.ts`.

**`DeprecationWarning: The 'punycode' module is deprecated`**

Harmless. It comes from a transitive dependency on Node 22 and does not affect
your agent.

## Next steps

This quickstart gets one agent answering in your terminal. To serve it over HTTP
instead of a REPL, see [Run an API server](/runtime/api-server/).

*   [Give your agent a tool that calls a real API](/tools-custom/function-tools/)
*   [Keep context across turns with session state](/sessions/state/)
*   [Split the work across several agents](/workflows/patterns/)
*   [Deploy your agent to Cloud Run](/deploy/cloud-run/)
*   [Build a complete agent step by step](/tutorials/)
