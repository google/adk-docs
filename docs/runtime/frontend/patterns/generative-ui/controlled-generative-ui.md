# Controlled

<div class="language-support-tag">
  <span class="lst-supported">CopilotKit pattern</span>
</div>

Use the controlled pattern when the agent should choose and fill
application-owned components during a run. The frontend registers the
components, and the ADK agent calls them as tools through CopilotKit.

Start from the [AG-UI setup](../../ag-ui/index.md) and the [React client](../../ag-ui/react.md).

## Register a render-only component

`useComponent` registers a component the agent can call only to render UI. It
does not run a backend handler.

```tsx title="RevenueCardComponent.tsx"
"use client";

import { useComponent } from "@copilotkit/react-core/v2";
import { z } from "zod";

function RevenueCard({
  title,
  value,
  trend,
}: {
  title: string;
  value: string;
  trend: string;
}) {
  return (
    <article>
      <h3>{title}</h3>
      <strong>{value}</strong>
      <p>{trend}</p>
    </article>
  );
}

export function RevenueCardComponent() {
  useComponent({
    name: "revenueCard",
    description: "Render a revenue KPI card in the application UI.",
    parameters: z.object({
      title: z.string(),
      value: z.string(),
      trend: z.string(),
    }),
    render: ({ title, value, trend }) => (
      <RevenueCard title={title} value={value} trend={trend} />
    ),
  });

  return null;
}
```

Mount the registration below `CopilotKit` and near the chat surface:

```tsx title="app/page.tsx"
"use client";

import { CopilotChat } from "@copilotkit/react-core/v2";
import { RevenueCardComponent } from "./RevenueCardComponent";

export default function Page() {
  return (
    <main style={{ height: "100vh" }}>
      <RevenueCardComponent />
      <CopilotChat agentId="default" />
    </main>
  );
}
```

## Agent instruction

Tell the ADK agent when to use the component. `AGUIToolset()` from the AG-UI
setup exposes registered client tools and components to the agent.

```python title="app.py"
from google.adk.agents import Agent
from ag_ui_adk import AGUIToolset

root_agent = Agent(
    name="assistant",
    model="gemini-2.5-flash",
    instruction=(
        "When the user asks for a KPI or dashboard summary, use the "
        "revenueCard tool instead of returning the card as plain text."
    ),
    tools=[AGUIToolset()],
)
```

Use [Declarative (A2UI)](a2ui.md) when the agent should compose a full structured surface
from a catalog, and use [Tool Rendering](tool-rendering.md) when you want to
render progress or results for ordinary tools.
