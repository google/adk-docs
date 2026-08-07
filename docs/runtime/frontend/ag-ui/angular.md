# Angular

<div class="language-support-tag">
  <span class="lst-supported">AG-UI client</span>
</div>

Use CopilotKit Angular when an Angular application should connect to an ADK
agent through AG-UI. CopilotKit owns the runtime connection and AG-UI client
behavior. Your Angular app talks to `/api/copilotkit`, not directly to the
Python `/ag-ui` endpoint.

## Install

Complete the [AG-UI runtime setup](index.md) first, then install the Angular
package:

```shell
npm install @copilotkit/angular
```

The Angular package expects Angular, Angular CDK, and RxJS to be provided by
your app.

## Runtime endpoint

Expose the same CopilotKit Runtime route used by the React guide:

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

## Provide CopilotKit

Configure CopilotKit in your Angular app config:

```ts title="app.config.ts"
import { ApplicationConfig } from "@angular/core";
import { provideCopilotKit } from "@copilotkit/angular";

export const appConfig: ApplicationConfig = {
  providers: [
    provideCopilotKit({
      runtimeUrl: "/api/copilotkit",
    }),
  ],
};
```

## Render chat

Use the packaged `copilot-chat` component for the default chat surface.

```ts title="chat.component.ts"
import { Component } from "@angular/core";
import { CopilotChat } from "@copilotkit/angular";

@Component({
  selector: "app-chat",
  standalone: true,
  imports: [CopilotChat],
  template: `
    <section style="height: 100vh">
      <copilot-chat [agentId]="'default'"></copilot-chat>
    </section>
  `,
})
export class ChatComponent {}
```

Use the lower-level Angular services and `injectAgentStore("default")` only
when you need a fully custom Angular chat surface. Keep the runtime bridge and
ADK middleware the same.
