# Human-in-the-loop

<div class="language-support-tag">
  <span class="lst-supported">CopilotKit pattern</span>
</div>

Use human-in-the-loop when an agent run must pause for a user decision before it
continues. CopilotKit renders the approval UI and sends the response back to the
agent through the same runtime boundary.

Start from the [AG-UI setup](../ag-ui/index.md) and the [React client](../ag-ui/react.md).

## Register an approval tool

`useHumanInTheLoop` registers a frontend tool that resolves only when your UI
calls `respond(...)`.

```tsx title="ApprovalTool.tsx"
"use client";

import { useHumanInTheLoop } from "@copilotkit/react-core/v2";
import { z } from "zod";

export function ApprovalTool() {
  useHumanInTheLoop({
    name: "approveRefund",
    description: "Ask the user to approve or deny a refund.",
    parameters: z.object({
      orderId: z.string(),
      amount: z.number(),
      reason: z.string(),
    }),
    render: ({ status, args, respond }) => {
      if (status !== "executing" || !respond) {
        return <p>Waiting for approval...</p>;
      }

      return (
        <section>
          <h3>Approve refund?</h3>
          <p>
            Order {args.orderId}: ${args.amount} for {args.reason}
          </p>
          <button onClick={() => respond({ approved: true })}>Approve</button>
          <button onClick={() => respond({ approved: false })}>Deny</button>
        </section>
      );
    },
  });

  return null;
}
```

Mount the tool below the provider:

```tsx title="app/page.tsx"
"use client";

import { CopilotChat } from "@copilotkit/react-core/v2";
import { ApprovalTool } from "./ApprovalTool";

export default function Page() {
  return (
    <main style={{ height: "100vh" }}>
      <ApprovalTool />
      <CopilotChat agentId="default" />
    </main>
  );
}
```

## Let the ADK agent request approval

`AGUIToolset()` exposes the frontend approval tool to the ADK agent. Keep the
tool name in the instruction exactly the same as the frontend registration.

```python title="app.py"
from google.adk.agents import Agent
from ag_ui_adk import AGUIToolset

root_agent = Agent(
    name="refund_assistant",
    model="gemini-2.5-flash",
    instruction=(
        "Before approving a refund, call approveRefund with the order id, "
        "amount, and reason. Continue only after the user responds."
    ),
    tools=[AGUIToolset()],
)
```

Every branch of the approval UI should call `respond(...)`. If the user can
close or navigate away from the approval UI, handle that as an explicit deny,
cancel, or timeout response so the agent run does not stay paused.
