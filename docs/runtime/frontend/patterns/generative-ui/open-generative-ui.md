# Open

<div class="language-support-tag">
  <span class="lst-supported">CopilotKit pattern</span>
</div>

Use the open pattern when the agent should generate a sandboxed interface
rather than choose from an application-owned component catalog. CopilotKit
provides the runtime middleware, tool registration, and sandbox renderer.

Start from the [AG-UI setup](../../ag-ui/index.md) and the [React client](../../ag-ui/react.md).

## Enable it in the runtime

Enable the open pattern on the CopilotKit Runtime route that already
registers your ADK AG-UI endpoint.

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
  openGenerativeUI: true,
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

With `openGenerativeUI` enabled, CopilotKit registers the
`generateSandboxedUi` tool and renders `open-generative-ui` activities in the
chat surface.

## Let the ADK agent use it

Expose CopilotKit frontend tools to the ADK agent with `AGUIToolset()` and tell
the model when generated UI is appropriate.

```python title="app.py"
from google.adk.agents import Agent
from ag_ui_adk import AGUIToolset

root_agent = Agent(
    name="ui_assistant",
    model="gemini-2.5-flash",
    instruction=(
        "When the user asks for an exploratory dashboard, interactive report, "
        "or one-off interface, call generateSandboxedUi. Use normal text for "
        "simple answers."
    ),
    tools=[AGUIToolset()],
)
```

No custom renderer is required in the React page:

```tsx title="app/page.tsx"
"use client";

import { CopilotChat } from "@copilotkit/react-core/v2";

export default function Page() {
  return (
    <main style={{ height: "100vh" }}>
      <CopilotChat agentId="default" />
    </main>
  );
}
```

## Use this for

- Exploratory dashboards or one-off views.
- Prototypes where the exact component catalog is not known.
- Sandboxed UI that should not get same-origin browser access.

Use [Controlled](controlled-generative-ui.md) or [Declarative (A2UI)](a2ui.md)
when you need the UI to stay inside a controlled application component catalog.
