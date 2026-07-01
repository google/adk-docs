# In-app Actions

<div class="language-support-tag">
  <span class="lst-supported">CopilotKit pattern</span>
</div>

Use in-app actions when the agent should trigger behavior inside the current
application: open a record, change a route, select an item, or start a local
workflow. The application owns the action and permissions; the ADK agent only
calls the tool exposed through CopilotKit.

Start from the [AG-UI setup](../ag-ui/index.md) and the [React client](../ag-ui/react.md).

## Register an app action

Use `useFrontendTool` for actions that must execute in the browser.

```tsx title="CustomerActions.tsx"
"use client";

import { useFrontendTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

export function CustomerActions({
  openCustomer,
}: {
  openCustomer: (customerId: string) => void;
}) {
  useFrontendTool(
    {
      name: "openCustomer",
      description: "Open a customer record in the application.",
      parameters: z.object({
        customerId: z.string(),
      }),
      handler: async ({ customerId }) => {
        openCustomer(customerId);
        return `Opened customer ${customerId}`;
      },
    },
    [openCustomer],
  );

  return null;
}
```

Mount the action registration below `CopilotKit`, next to the chat surface:

```tsx title="app/page.tsx"
"use client";

import { CopilotChat } from "@copilotkit/react-core/v2";
import { CustomerActions } from "./CustomerActions";

export default function Page() {
  return (
    <main style={{ height: "100vh" }}>
      <CustomerActions openCustomer={(id) => console.log("open", id)} />
      <CopilotChat agentId="default" />
    </main>
  );
}
```

## Expose the action to ADK

`AGUIToolset()` exposes CopilotKit frontend tools to the ADK agent.

```python title="app.py"
from google.adk.agents import Agent
from ag_ui_adk import AGUIToolset

root_agent = Agent(
    name="crm_assistant",
    model="gemini-2.5-flash",
    instruction=(
        "When the user asks to inspect a customer, call openCustomer with the "
        "customer id. Do not claim the customer is open until the tool returns."
    ),
    tools=[AGUIToolset()],
)
```

Use [Shared State](shared-state.md) when the agent also needs to read or update
application state across turns.
