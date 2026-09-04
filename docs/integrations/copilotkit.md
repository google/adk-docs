---
catalog_title: CopilotKit
catalog_description: Add React, Angular, Vue, mobile, and Slack frontends to your agents
catalog_icon: /integrations/assets/copilotkit.png
---

# CopilotKit user interface for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[CopilotKit](https://github.com/CopilotKit/CopilotKit) is an open source set of
frontend libraries and a runtime that connect applications to agents over
[AG-UI](/integrations/ag-ui/). With ADK, the `ag-ui-adk` package exposes your
agent as an AG-UI endpoint, and CopilotKit gives that endpoint a chat surface,
frontend tools, generative UI, and human-in-the-loop controls in React, Angular,
Vue, React Native, or Slack.

The [AG-UI integration page](/integrations/ag-ui/) covers the protocol and a
`create` command that scaffolds a full-stack sample. This page shows how to add
CopilotKit to an existing ADK project.

## Use cases

- **Chat surface**: Stream an ADK agent's messages, tool calls, and reasoning
  into a packaged chat component for web or mobile apps.
- **Frontend tools**: Let the agent call functions that run in the browser, such
  as navigating, opening a record, or reading application state.
- **Generative UI**: Render tool calls and results with application components
  instead of plain text.
- **Human-in-the-loop**: Pause an agent run until the user approves, edits, or
  rejects a proposed action, then resume with the answer.
- **Messaging channels**: Run the same agent in Slack with the open source
  Channels SDK.

## Prerequisites

- Python 3.10 to 3.14 and Node.js 18 or later
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey),
  exported as `GOOGLE_API_KEY`
- A React application, such as Next.js, for the frontend steps below

## Installation

Install the backend packages:

```bash
pip install google-adk ag-ui-adk fastapi "uvicorn[standard]"
```

Install the frontend packages in your web application:

```bash
npm install @copilotkit/react-core @copilotkit/runtime @ag-ui/client hono zod
```

## Use with agent

### 1. Expose the agent over AG-UI

```python title="agent.py"
from fastapi import FastAPI
from google.adk.agents import Agent
from google.adk.apps import App, ResumabilityConfig

from ag_ui_adk import ADKAgent, AGUIToolset, add_adk_fastapi_endpoint

root_agent = Agent(
    model="gemini-flash-latest",
    name="copilotkit_agent",
    instruction=(
        "You are a helpful assistant. Use the frontend tools when they fit "
        "the request."
    ),
    tools=[AGUIToolset()],
)

adk_app = App(
    name="copilotkit_app",
    root_agent=root_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)

ag_ui_agent = ADKAgent.from_app(
    adk_app,
    user_id="local_user",
    use_in_memory_services=True,
)

app = FastAPI()
add_adk_fastapi_endpoint(app, ag_ui_agent, path="/ag-ui")
```

The `AGUIToolset()` toolset makes tools registered in the frontend callable by
the agent. Creating the middleware with `ADKAgent.from_app()` and
`ResumabilityConfig` lets a run pause on a frontend tool call and resume when
the result arrives.

Start the backend:

```bash
uvicorn agent:app --reload --port 8000
```

### 2. Register the endpoint with CopilotKit Runtime

CopilotKit Runtime runs inside your web application and forwards AG-UI runs to
the ADK endpoint. In a Next.js app, add a route:

```typescript title="app/api/copilotkit/[[...slug]]/route.ts"
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

### 3. Render chat

Mount the provider once near the root of the React tree, then place the chat
component anywhere below it:

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

The `CopilotChat` component handles message state, streaming, tool call
display, attachments, and suggestions.

### 4. Add a frontend tool

Register a tool in the browser. The `AGUIToolset()` on the ADK side exposes it
to the agent on every run:

```tsx title="app/SearchTool.tsx"
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
    handler: async ({ query }) => {
      const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
      return response.text();
    },
  });

  return null;
}
```

Render `<SearchTool />` below the provider, next to `<CopilotChat />`.

## Available hooks

Hook | Description
---- | -----------
`useFrontendTool` | Register a tool that executes in the browser and returns its result to the agent
`useRenderTool` | Render progress and results for a backend tool by name
`useComponent` | Register a render-only component the agent can place in the chat
`useHumanInTheLoop` | Register a tool whose UI must call `respond()` before the run continues
`useAgentContext` | Share application state with the agent as context on every run
`useAgent` | Read messages, state, and run status when building a custom chat surface

All hooks are exported from `@copilotkit/react-core/v2`. See the
[CopilotKit hook reference](https://docs.copilotkit.ai/reference/hooks/useFrontendTool)
for parameters and return values.

## Other clients

The same CopilotKit Runtime route and ADK endpoint serve every CopilotKit
client:

- **Angular**: the `@copilotkit/angular` package with `provideCopilotKit()` and
  the `<copilot-chat>` component. See the
  [Angular guide](https://docs.copilotkit.ai/angular).
- **Vue**: the `@copilotkit/vue` package with `CopilotKitProvider` and
  `CopilotChat`. See the [Vue guide](https://docs.copilotkit.ai/vue).
- **React Native**: the `@copilotkit/react-native` package with headless hooks
  and an optional packaged chat under `@copilotkit/react-native/components`.
  See the [React Native guide](https://docs.copilotkit.ai/react-native).

## Messaging channels

The open source Channels SDK connects a Slack workspace directly to the
`ag-ui-adk` endpoint. It does not need the CopilotKit Runtime route:

```bash
npm install @copilotkit/bot @copilotkit/bot-slack @copilotkit/bot-ui
```

```typescript title="slack-bot.ts"
import { createBot } from "@copilotkit/bot";
import {
  defaultSlackContext,
  defaultSlackTools,
  SanitizingHttpAgent,
  slack,
} from "@copilotkit/bot-slack";

const bot = createBot({
  adapters: [
    slack({
      botToken: process.env.SLACK_BOT_TOKEN!,
      appToken: process.env.SLACK_APP_TOKEN!,
    }),
  ],
  agent: (threadId) => {
    const agent = new SanitizingHttpAgent({
      url: process.env.ADK_AG_UI_URL ?? "http://localhost:8000/ag-ui",
    });
    agent.threadId = threadId;
    return agent;
  },
  tools: [...defaultSlackTools],
  context: [...defaultSlackContext],
});

bot.onMention(({ thread }) => thread.runAgent());

await bot.start();
```

The adapter runs in Socket Mode by default, so local development needs an
app-level token but no public URL. Each Slack thread maps to one AG-UI thread,
and Block Kit rendering, interactions, and approvals are handled by the
adapter. See the [Channels documentation](https://docs.copilotkit.ai/slack)
for Slack app settings and self-hosted deployment.

## Additional resources

- [CopilotKit documentation for ADK](https://docs.copilotkit.ai/adk)
- [CopilotKit on GitHub](https://github.com/CopilotKit/CopilotKit)
- [ADK middleware for AG-UI (`ag-ui-adk`) on PyPI](https://pypi.org/project/ag-ui-adk/)
- [ADK middleware source](https://github.com/ag-ui-protocol/ag-ui/tree/main/integrations/adk-middleware)
- [AG-UI Dojo](https://dojo.ag-ui.com) with live ADK examples
