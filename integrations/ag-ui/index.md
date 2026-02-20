# AG-UI user interface for ADK

Supported in ADKPythonTypeScriptGoJava

Turn your ADK agents into full-featured applications with rich, responsive UIs. [AG-UI](https://docs.ag-ui.com/) is an open protocol that handles streaming events, client state, and bi-directional communication between your agents and users.

[AG-UI](https://github.com/ag-ui-protocol/ag-ui) provides a consistent interface to empower rich clients across technology stacks, from mobile to the web and even the command line. There are a number of different clients that support AG-UI:

- [CopilotKit](https://copilotkit.ai) provides tooling and components to tightly integrate your agent with web applications
- Clients for [Kotlin](https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/kotlin), [Java](https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/java), [Go](https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/go/example/client), and [CLI implementations](https://github.com/ag-ui-protocol/ag-ui/tree/main/apps/client-cli-example/src) in TypeScript

This tutorial uses CopilotKit to create a sample app backed by an ADK agent that demonstrates some of the features supported by AG-UI.

## Quickstart

To get started, let's create a sample application with an ADK agent and a simple web client:

1. Create the app:

   ```bash
   npx copilotkit@latest create -f adk
   ```

1. Set your Google API key:

   ```bash
   export GOOGLE_API_KEY="your-api-key"
   ```

1. Install dependencies and run:

   ```bash
   npm install && npm run dev
   ```

This starts two servers:

- **http://localhost:3000** - The web UI (open this in your browser)
- **http://localhost:8000** - The ADK agent API (backend only)

Open <http://localhost:3000> in your browser to chat with your agent.

## Features

### Chat

Chat is a familiar interface for exposing your agent, and AG-UI handles streaming messages between your users and agents:

src/app/page.tsx

```tsx
<CopilotSidebar
  clickOutsideToClose={false}
  defaultOpen={true}
  labels={{
    title: "Popup Assistant",
    initial: "👋 Hi, there! You're chatting with an agent. This agent comes with a few tools to get you started..."
  }}
/>
```

Learn more about the chat UI [in the CopilotKit docs](https://docs.copilotkit.ai/adk/agentic-chat-ui).

### Generative UI

AG-UI lets you share tool information with a Generative UI so that it can be displayed to users:

src/app/page.tsx

```tsx
useRenderToolCall(
  {
    name: "get_weather",
    description: "Get the weather for a given location.",
    parameters: [{ name: "location", type: "string", required: true }],
    render: ({ args }) => {
      return <WeatherCard location={args.location} themeColor={themeColor} />;
    },
  },
  [themeColor],
);
```

Learn more about Generative UI [in the CopilotKit docs](https://docs.copilotkit.ai/adk/generative-ui).

### Shared State

ADK agents can be stateful, and synchronizing that state between your agents and your UIs enables powerful and fluid user experiences. State can be synchronized both ways so agents are automatically aware of changes made by your user or other parts of your application:

src/app/page.tsx

```tsx
const { state, setState } = useCoAgent<AgentState>({
  name: "my_agent",
  initialState: {
    proverbs: [
      "A journey of a thousand miles begins with a single step.",
    ],
  },
})
```

Learn more about shared state [in the CopilotKit docs](https://docs.copilotkit.ai/adk/shared-state).

## Resources

To see what other features you can build into your UI with AG-UI, refer to the CopilotKit docs:

- [Agentic Generative UI](https://docs.copilotkit.ai/adk/generative-ui/agentic)
- [Human in the Loop](https://docs.copilotkit.ai/adk/human-in-the-loop)
- [Frontend Actions](https://docs.copilotkit.ai/adk/frontend-actions)

Or try them out in the [AG-UI Dojo](https://dojo.ag-ui.com).
