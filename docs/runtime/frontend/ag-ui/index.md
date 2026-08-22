# AG-UI

<div class="language-support-tag">
  <span class="lst-supported">Supported middleware</span><span class="lst-python">Python example</span>
</div>

AG-UI is the client-facing event protocol used between CopilotKit Runtime and
agent backends. With ADK, use the `ag-ui-adk` package to expose an ADK agent as
an AG-UI endpoint, then register that endpoint in CopilotKit Runtime.

Application clients should connect to CopilotKit Runtime. They should not call
the Python AG-UI endpoint directly unless you are building and maintaining your
own AG-UI client.

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
    model="gemini-2.5-flash",
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

`AGUIToolset()` lets the ADK agent call tools supplied by CopilotKit clients.
`ADKAgent.from_app(...)` keeps client tools and human-in-the-loop runs resumable.

Run the backend:

```shell
uvicorn app:app --reload --port 8000
```

The ADK agent now accepts AG-UI runs at `http://localhost:8000/ag-ui`.

## Add CopilotKit Runtime

In the web app that hosts your frontend, register the ADK AG-UI endpoint with
CopilotKit Runtime:

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

Your application clients now use `/api/copilotkit`. CopilotKit Runtime handles
the AG-UI transport to the ADK backend.

## Connect a client

After the runtime route is available, add a CopilotKit client:

- [React](react.md)
- [Angular](angular.md)
- [Vue](vue.md)
- [React Native](react-native.md)
- [Slack](slack.md)

Use [A2UI](../a2ui.md) when the agent should render structured UI, and use the
[patterns](../patterns/generative-ui/controlled-generative-ui.md) pages when the client needs tools,
custom renderers, MCP Apps, or human-in-the-loop controls.
