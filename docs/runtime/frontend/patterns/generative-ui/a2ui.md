# Declarative (A2UI)

<div class="language-support-tag">
  <span class="lst-supported">CopilotKit pattern</span>
</div>

Use Declarative (A2UI) when the agent should create a structured UI surface
from a component catalog. In the CopilotKit path, you provide the catalog to the
provider and the ADK AG-UI adapter handles the A2UI tool path.

Start from the [AG-UI setup](../../ag-ui/index.md) and the [A2UI overview](../../a2ui.md).

## Provide the catalog

Create a small catalog module with the component implementations your app can
render. The catalog id is the stable name the agent and renderer use for the
same component set.

```ts title="a2ui-catalog.ts"
import { Catalog } from "@copilotkit/a2ui-renderer";
import type { ReactComponentImplementation } from "@copilotkit/a2ui-renderer";

import { MetricCard, SalesTable } from "./a2ui-renderers";

export const salesCatalog = new Catalog<ReactComponentImplementation>(
  "https://example.com/catalogs/sales.json",
  [MetricCard, SalesTable],
  [],
);
```

Then pass that catalog to the provider.

```tsx title="app/providers.tsx"
"use client";

import { CopilotKit } from "@copilotkit/react-core/v2";
import "@copilotkit/react-core/v2/styles.css";

import { salesCatalog } from "./a2ui-catalog";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <CopilotKit
      runtimeUrl="/api/copilotkit"
      useSingleEndpoint={false}
      a2ui={{ catalog: salesCatalog }}
    >
      {children}
    </CopilotKit>
  );
}
```

When a catalog is present, CopilotKit enables the A2UI renderer, forwards
catalog context with the run, and renders `a2ui-surface` activities in
`CopilotChat`.

## Configure the ADK wrapper

For dynamic A2UI, configure `ADKAgent` with the catalog id and composition
guidelines. Do not manually add A2UI tools to the ADK agent.

```python title="app.py"
from google.adk.agents import Agent
from ag_ui_adk import ADKAgent

root_agent = Agent(
    name="a2ui_assistant",
    model="gemini-2.5-pro",
    instruction=(
        "When a visual answer is useful, create an A2UI surface from the "
        "available catalog. Keep the text response brief."
    ),
)

ag_ui_agent = ADKAgent(
    adk_agent=root_agent,
    app_name="a2ui_app",
    user_id="local_user",
    session_timeout_seconds=3600,
    use_in_memory_services=True,
    a2ui={
        "default_catalog_id": "https://example.com/catalogs/sales.json",
        "guidelines": {
            "composition_guide": "Use KPI cards for metrics and tables for row data.",
        },
    },
)
```

The FastAPI endpoint is the same `add_adk_fastapi_endpoint(...)` setup from the
[AG-UI overview](../../ag-ui/index.md).

## When to use fixed output

If your application already knows the component tree, the agent can call a
normal ADK backend tool that returns an A2UI operations envelope. Use that for
stable layouts such as flight results, approval forms, or order tables.

For dynamic UI, prefer the provider catalog plus ADK wrapper configuration
above. CopilotKit and the adapter manage the generated A2UI operations.
