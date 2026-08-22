# React Native

<div class="language-support-tag">
  <span class="lst-supported">Mobile client</span>
</div>

Use CopilotKit React Native when a native mobile app should connect to an ADK
agent through AG-UI. The React Native package is headless: it provides the
provider and hooks, and you build the UI with React Native components.
If you want a packaged mobile chat surface, import it from
`@copilotkit/react-native/components`.

## Install

Complete the [AG-UI runtime setup](index.md) first, then install the React
Native package:

```shell
npm install @copilotkit/react-native
```

## Runtime endpoint

Host CopilotKit Runtime from a reachable backend. A local emulator cannot use a
relative `/api/copilotkit` URL unless your development proxy forwards it.

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

## Add polyfills

Import the React Native polyfills before the app starts:

```js title="index.js"
import "@copilotkit/react-native/polyfills";

import { AppRegistry } from "react-native";
import App from "./App";
import { name as appName } from "./app.json";

AppRegistry.registerComponent(appName, () => App);
```

## Add the provider

Point the provider at the deployed runtime URL:

```tsx title="App.tsx"
import {
  CopilotKitProvider,
  useAgent,
  useCopilotKit,
} from "@copilotkit/react-native";
import { useState } from "react";
import { Button, TextInput, View } from "react-native";

export default function App() {
  return (
    <CopilotKitProvider runtimeUrl="https://your-domain.com/api/copilotkit">
      <ChatScreen />
    </CopilotKitProvider>
  );
}

function ChatScreen() {
  const [text, setText] = useState("");
  const { agent } = useAgent({ agentId: "default" });
  const { copilotkit } = useCopilotKit();

  async function send() {
    const content = text.trim();
    if (!content) return;

    agent.addMessage({
      id: crypto.randomUUID(),
      role: "user",
      content,
    });
    setText("");

    await copilotkit.runAgent({ agent });
  }

  return (
    <View>
      <TextInput value={text} onChangeText={setText} />
      <Button title="Send" onPress={send} disabled={agent.isRunning} />
    </View>
  );
}
```

Render `agent.messages` with your own React Native components. Use the same
hooks as the React client for frontend tools, component rendering, and
human-in-the-loop flows.

If you prefer the packaged mobile chat UI, render the component from the
components subpath:

```tsx
import { CopilotChat } from "@copilotkit/react-native/components";

<CopilotChat agentName="default" headerTitle="Assistant" />;
```
