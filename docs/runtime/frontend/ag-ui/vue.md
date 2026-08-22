# Vue

<div class="language-support-tag">
  <span class="lst-supported">AG-UI client</span>
</div>

Use CopilotKit Vue when a Vue 3 application should connect to an ADK agent
through AG-UI. CopilotKit owns the runtime connection, streaming, and chat
state. Your Vue app talks to `/api/copilotkit`.

## Install

Complete the [AG-UI runtime setup](index.md) first, then install the Vue
package:

```shell
npm install @copilotkit/vue @copilotkit/core
```

## Runtime endpoint

Expose a CopilotKit Runtime route that registers the ADK AG-UI endpoint:

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

## Add the Vue client

Import the stylesheet once in your app entry:

```ts title="src/main.ts"
import { createApp } from "vue";
import App from "./App.vue";
import "@copilotkit/vue/styles.css";

createApp(App).mount("#app");
```

Wrap the assistant surface with `CopilotKitProvider` and render `CopilotChat`:

```vue title="src/App.vue"
<script setup lang="ts">
import { CopilotKitProvider, CopilotChat } from "@copilotkit/vue";
</script>

<template>
  <CopilotKitProvider runtime-url="/api/copilotkit">
    <main style="height: 100vh">
      <CopilotChat agent-id="default" />
    </main>
  </CopilotKitProvider>
</template>
```

Use Vue slots and composables when you need custom message, activity, or tool
rendering. Keep the CopilotKit runtime route and the ADK AG-UI backend the same.
