# MCP Apps

<div class="language-support-tag">
  <span class="lst-supported">CopilotKit pattern</span>
</div>

Use MCP Apps when a tool result should render an interactive MCP-provided app
inside the CopilotKit surface. CopilotKit includes runtime middleware and a
built-in renderer for `mcp-apps` activity messages.

Start from the [AG-UI setup](../../ag-ui/index.md) and the [React client](../../ag-ui/react.md).

## Register the MCP app server

Configure MCP Apps on `CopilotRuntime`. This is runtime-level middleware, not a
separate agent.

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
  mcpApps: {
    servers: [
      {
        type: "http",
        url: process.env.MCP_SERVER_URL ?? "http://localhost:3108/mcp",
      },
    ],
  },
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

## Create the MCP app

Build and host the MCP app server separately, following the
[MCP Apps protocol](https://github.com/modelcontextprotocol/ext-apps)
from the Model Context Protocol organization. The app server owns the UI
resource, tool metadata, and MCP transport. This page assumes that server is
running and available at `MCP_SERVER_URL`.

## Let the ADK agent use it

`AGUIToolset()` exposes the MCP app tool forwarded by CopilotKit Runtime to the
ADK agent. Use the tool name defined by your MCP app server.

```python title="app.py"
from google.adk.agents import Agent
from ag_ui_adk import AGUIToolset

root_agent = Agent(
    name="orders_assistant",
    model="gemini-2.5-flash",
    instruction=(
        "When the user asks to inspect an order, call show_order_status with "
        "the order id so the MCP app can render the interactive UI."
    ),
    tools=[AGUIToolset()],
)
```

## Client setup

No custom renderer is needed for the default CopilotKit chat surface:

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

When the backend emits an MCP Apps activity, CopilotKit renders it with the
built-in MCP Apps renderer and routes app messages back through the active
agent.

## Backend boundary

Keep MCP server credentials and tool policy in the backend. The frontend should
only render MCP Apps activities that arrive through CopilotKit Runtime.

Use this pattern when the interaction belongs in an MCP app. Use
[Tool Rendering](tool-rendering.md) when the app only needs to show progress or
results for a normal tool call.
