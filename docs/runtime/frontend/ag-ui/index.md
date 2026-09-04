# AG-UI

<div class="language-support-tag">
  <span class="lst-supported">Supported middleware</span><span class="lst-python">Python example</span>
</div>

[AG-UI](https://docs.ag-ui.com/) is an open, event-based protocol between agent
backends and user-facing clients. It standardizes streaming text, tool calls,
shared state, and the run lifecycle, so a frontend can work with any agent
framework that emits AG-UI events. With ADK, the `ag-ui-adk` package exposes an
ADK agent as an AG-UI endpoint.

This page sets up the endpoint. The [Frontends overview](../index.md) lists
clients that can connect to it.

## Install the ADK middleware

Use Python 3.10 through 3.14.

```shell
pip install google-adk ag-ui-adk fastapi "uvicorn[standard]"
```

Set your Google API key before starting the server:

```shell
export GOOGLE_API_KEY="your-api-key"
```

Create the ADK AG-UI endpoint:

```python title="app.py"
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.adk.agents import Agent
from google.adk.apps import App, ResumabilityConfig

from ag_ui_adk import ADKAgent, AGUIToolset, add_adk_fastapi_endpoint


root_agent = Agent(
    name="assistant",
    model="gemini-flash-latest",
    instruction="You are a helpful ADK assistant.",
    tools=[AGUIToolset()],
)

adk_app = App(
    name="adk_ag_ui_app",
    root_agent=root_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)

ag_ui_agent = ADKAgent.from_app(
    adk_app,
    user_id="local_user",
    session_timeout_seconds=3600,
    use_in_memory_services=True,
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:4200",
        "http://localhost:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)
add_adk_fastapi_endpoint(app, ag_ui_agent, path="/ag-ui")
```

The `AGUIToolset()` toolset lets the ADK agent call tools that the connected
client registers, such as browser actions or approval dialogs. Creating the
middleware with `ADKAgent.from_app(...)` and `ResumabilityConfig` keeps those
client tool calls resumable: the run pauses while the client works and resumes
when the result arrives.

Run the backend:

```shell
uvicorn app:app --reload --port 8000
```

The ADK agent now accepts AG-UI runs at `http://localhost:8000/ag-ui`.

## What the endpoint emits

Each run streams Server-Sent Events. The event types a frontend handles most
often are:

| Event | Meaning |
|---|---|
| `RUN_STARTED`, `RUN_FINISHED`, `RUN_ERROR` | Run lifecycle. |
| `TEXT_MESSAGE_START`, `TEXT_MESSAGE_CONTENT`, `TEXT_MESSAGE_END` | Streaming assistant text. |
| `TOOL_CALL_START`, `TOOL_CALL_ARGS`, `TOOL_CALL_END`, `TOOL_CALL_RESULT` | Tool calls, including client tools the frontend must execute. |
| `STATE_SNAPSHOT`, `STATE_DELTA` | Shared state, with deltas encoded as JSON Patch. |
| `MESSAGES_SNAPSHOT` | The full message history for the thread. Emitted only when the middleware is created with `emit_messages_snapshot=True`. |

See the [AG-UI event reference](https://docs.ag-ui.com/concepts/events) for
the complete list.

## Connect a client

=== "CopilotKit"

    CopilotKit Runtime runs inside your web application and forwards AG-UI
    runs to the ADK endpoint. Register the endpoint once, and every CopilotKit
    client connects to the runtime route.

    ```shell
    npm install @copilotkit/runtime @ag-ui/client hono
    ```

    ```ts title="app/api/copilotkit/[[...slug]]/route.ts"
    import { HttpAgent } from "@ag-ui/client";
    import {
      CopilotRuntime,
      InMemoryAgentRunner,
      createCopilotEndpoint,
    } from "@copilotkit/runtime/v2";
    import { handle } from "hono/vercel";

    const runtime = new CopilotRuntime({
      agents: {
        default: new HttpAgent({
          url: process.env.ADK_AG_UI_URL ?? "http://localhost:8000/ag-ui",
        }),
      },
      runner: new InMemoryAgentRunner(),
    });

    const app = createCopilotEndpoint({
      runtime,
      basePath: "/api/copilotkit",
    });

    export const GET = handle(app);
    export const POST = handle(app);
    export const PATCH = handle(app);
    export const DELETE = handle(app);
    ```

    Application clients now use `/api/copilotkit`. See the
    [CopilotKit integration](/integrations/copilotkit/) page for the React
    provider, chat component, and frontend tools.

=== "Any AG-UI client"

    Post a run to the endpoint and read the event stream:

    ```shell
    curl -N http://localhost:8000/ag-ui \
      -H "Content-Type: application/json" \
      -H "Accept: text/event-stream" \
      -d '{
        "threadId": "thread-1",
        "runId": "run-1",
        "messages": [{"id": "msg-1", "role": "user", "content": "Hello"}],
        "tools": [],
        "context": [],
        "state": {},
        "forwardedProps": {}
      }'
    ```

    The AG-UI client SDKs for TypeScript, Kotlin, Java, and Go wrap this
    request and parse the events for you. See the
    [Frontends overview](../index.md) for links.
