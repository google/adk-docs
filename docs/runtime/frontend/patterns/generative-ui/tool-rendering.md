# Tool Rendering

<div class="language-support-tag">
  <span class="lst-supported">CopilotKit pattern</span>
</div>

Use tool rendering when the agent calls a normal tool and the frontend should
show progress or results with application UI.

Start from the [AG-UI setup](../../ag-ui/index.md) and the [React client](../../ag-ui/react.md).

## Add the ADK tool

Tool rendering starts with a normal backend tool on the ADK agent.

```python title="app.py"
from google.adk.agents import Agent


def search_docs(query: str) -> str:
    """Search product documentation for a user query."""
    return f"Top result for {query}: AG-UI connects ADK agents to frontends."


root_agent = Agent(
    name="docs_assistant",
    model="gemini-2.5-flash",
    instruction=(
        "When the user asks a documentation question, call search_docs and "
        "summarize the result."
    ),
    tools=[search_docs],
)
```

## Render a tool call

Register a renderer for the tool name:

```tsx title="SearchRenderer.tsx"
"use client";

import { useRenderTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

export function SearchRenderer() {
  useRenderTool({
    name: "search_docs",
    parameters: z.object({
      query: z.string(),
    }),
    render: ({ status, parameters, result }) => {
      if (status === "inProgress") {
        return <p>Preparing search...</p>;
      }

      if (status === "executing") {
        return <p>Searching for {parameters.query}...</p>;
      }

      return <pre>{String(result)}</pre>;
    },
  });

  return null;
}
```

Mount the renderer below `CopilotKit`:

```tsx title="app/page.tsx"
"use client";

import { CopilotChat } from "@copilotkit/react-core/v2";
import { SearchRenderer } from "./SearchRenderer";

export default function Page() {
  return (
    <main style={{ height: "100vh" }}>
      <SearchRenderer />
      <CopilotChat agentId="default" />
    </main>
  );
}
```

Use `useFrontendTool` when the tool should execute in the browser. Use
`useRenderTool` when the tool already exists in the backend and only needs a
frontend renderer.
