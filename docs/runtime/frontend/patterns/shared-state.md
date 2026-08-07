# Shared State

<div class="language-support-tag">
  <span class="lst-supported">CopilotKit pattern</span>
</div>

Use shared state when user or application state should be visible to the ADK
agent during a run. CopilotKit sends the state as agent context, and frontend
tools can update browser-owned state when the agent needs to change the current
UI.

Keep authoritative business state in your backend or storage layer. Shared
frontend state is for screen state, drafts, filters, selections, and other
client-owned context.

Start from the [AG-UI setup](../ag-ui/index.md) and the [React client](../ag-ui/react.md).

## Share client state

Use `useAgentContext` for read access and `useFrontendTool` for controlled
updates. The tool name is the contract the ADK agent will call.

```tsx title="OrderDraftState.tsx"
"use client";

import {
  CopilotChat,
  useAgentContext,
  useFrontendTool,
} from "@copilotkit/react-core/v2";
import { useMemo, useState } from "react";
import { z } from "zod";

type OrderDraft = {
  customerId: string;
  deliveryDate: string;
  notes: string;
};

export function OrderDraftState() {
  const [orderDraft, setOrderDraft] = useState<OrderDraft>({
    customerId: "cust_123",
    deliveryDate: "2026-07-08",
    notes: "Leave at the front desk.",
  });

  const sharedState = useMemo(
    () => ({
      orderDraft,
      selectedScreen: "order-draft",
    }),
    [orderDraft],
  );

  useAgentContext({
    description:
      "Current browser-owned order draft. This is not saved until the user confirms.",
    value: sharedState,
  });

  useFrontendTool(
    {
      name: "updateOrderDraft",
      description:
        "Update the browser-owned order draft. Do not use this to save the final order.",
      parameters: z.object({
        deliveryDate: z.string().optional(),
        notes: z.string().optional(),
      }),
      handler: async ({ deliveryDate, notes }) => {
        setOrderDraft((current) => ({
          ...current,
          deliveryDate: deliveryDate ?? current.deliveryDate,
          notes: notes ?? current.notes,
        }));

        return { status: "updated" };
      },
    },
    [],
  );

  return <CopilotChat agentId="default" />;
}
```

Mount the state component below `CopilotKit`, near the chat surface:

```tsx title="app/page.tsx"
"use client";

import { OrderDraftState } from "./OrderDraftState";

export default function Page() {
  return (
    <main style={{ height: "100vh" }}>
      <OrderDraftState />
    </main>
  );
}
```

## Let the ADK agent use it

`AGUIToolset()` exposes the registered frontend tool to the ADK agent. Keep the
tool name in the instruction exactly the same as the frontend registration.

```python title="app.py"
from fastapi import FastAPI
from google.adk.agents import Agent
from google.adk.apps import App, ResumabilityConfig

from ag_ui_adk import ADKAgent, AGUIToolset, add_adk_fastapi_endpoint


root_agent = Agent(
    name="assistant",
    model="gemini-2.5-flash",
    instruction=(
        "Use the provided shared context to understand the current order draft. "
        "When the user asks to change the draft delivery date or notes, call "
        "the updateOrderDraft frontend tool. Do not claim that an order is "
        "saved or submitted unless a backend storage tool or API confirms it."
    ),
    tools=[AGUIToolset()],
)

adk_app = App(
    name="shared_state_app",
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
add_adk_fastapi_endpoint(app, ag_ui_agent, path="/ag-ui")
```

For durable changes, add normal backend tools or API calls on the ADK side and
keep `updateOrderDraft` limited to the user's current browser session.
