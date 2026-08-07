# React

<div class="language-support-tag">
  <span class="lst-supported">AG-UI client</span>
</div>

Use CopilotKit React when a browser UI should connect to an ADK agent through
AG-UI. CopilotKit owns the client-side protocol handling, streaming messages,
tool calls, state updates, and chat UI. Your React code talks to
`/api/copilotkit`, not directly to the Python `/ag-ui` endpoint.

## Install

Complete the [AG-UI runtime setup](index.md) first, then install the React
client package:

```shell
npm install @copilotkit/react-core zod
```

## Runtime endpoint

The React app needs a CopilotKit Runtime route that registers the ADK AG-UI
endpoint:

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

## Add the provider

Mount `CopilotKit` once near the React root.

```tsx title="app/providers.tsx"
"use client";

import { CopilotKit } from "@copilotkit/react-core/v2";
import "@copilotkit/react-core/v2/styles.css";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit" useSingleEndpoint={false}>
      {children}
    </CopilotKit>
  );
}
```

Use the provider from your root layout:

```tsx title="app/layout.tsx"
import { Providers } from "./providers";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

## Render chat

Add `CopilotChat` anywhere below the provider:

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

`CopilotChat` manages message state, input state, streaming, tool calls,
attachments, and suggestions internally.

## Add browser tools

Use `useFrontendTool` when the ADK agent should call a browser-side capability.
`AGUIToolset()` on the ADK side exposes these tools to the agent.

```tsx title="SearchTool.tsx"
"use client";

import { useFrontendTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

export function SearchTool() {
  useFrontendTool({
    name: "searchDocs",
    description: "Search the current application documentation.",
    parameters: z.object({
      query: z.string(),
    }),
    handler: async ({ query }, { signal }) => {
      const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`, {
        signal,
      });
      return response.text();
    },
  });

  return null;
}
```

For richer UI, continue with [Controlled](../patterns/generative-ui/controlled-generative-ui.md),
[Declarative (A2UI)](../patterns/generative-ui/a2ui.md), [Tool Rendering](../patterns/generative-ui/tool-rendering.md),
or [Human-in-the-loop](../patterns/human-in-the-loop.md).
