# Building chat experiences with AG-UI and CopilotKit

## Overview

As an agent builder, you want users to interact with your agents through a rich
and responsive interface. Building UIs from scratch requires a lot of effort,
especially to support streaming events and client state. That's exactly what
[AG-UI](https://docs.ag-ui.com/) was designed for - rich user experiences
directly connected to an agent.

[AG-UI](https://github.com/ag-ui-protocol/ag-ui) provides a consistent interface
to empower rich clients across technology stacks, from mobile to the web and
even the command line. There are a number of different clients that support
AG-UI:

- [CopilotKit](https://copilotkit.ai) provides tooling and components to tightly integrate your agent with web applications
- Clients for [Kotlin](https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/kotlin), [Java](https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/java), [Go](https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/go/example/client), and [CLI implementations](https://github.com/ag-ui-protocol/ag-ui/tree/main/apps/client-cli-example/src) in TypeScript

This tutorial uses CopilotKit to create a sample app backed by an ADK agent that
demonstrates some of the features supported by AG-UI.

## Quickstart

To get started, let's create a sample application with an ADK agent and a simple
web client:

```
npx create-ag-ui-app@latest --adk
```

### Chat

Chat is a familiar interface for exposing your agent, and AG-UI handles
streaming messages between your users and agents:

```tsx title="src/app/page.tsx"
<CopilotSidebar
  clickOutsideToClose={false}
  defaultOpen={true}
  labels={{
    title: "Popup Assistant",
    initial: "👋 Hi, there! You're chatting with an agent. This agent comes with a few tools to get you started..."
  }}
/>
```

Learn more about the chat UI
[in the CopilotKit docs](https://docs.copilotkit.ai/adk/agentic-chat-ui).

### Tool Based Generative UI (Rendering Tools)

AG-UI lets you share tool information with a Generative UI so that it can be
displayed to users:

```tsx title="src/app/page.tsx"
useCopilotAction({
  name: "get_weather",
  description: "Get the weather for a given location.",
  available: "disabled",
  parameters: [
    { name: "location", type: "string", required: true },
  ],
  render: ({ args }) => {
    return <WeatherCard location={args.location} themeColor={themeColor} />
  },
});
```

Learn more about the Tool-based Generative UI
[in the CopilotKit docs](https://docs.copilotkit.ai/adk/generative-ui/tool-based).

### Shared State

ADK agents can be stateful, and synchronizing that state between your agents and
your UIs enables powerful and fluid user experiences. State can be synchronized
both ways so agents are automatically aware of changes made by your user or
other parts of your application:

```tsx title="src/app/page.tsx"
const { state, setState } = useCoAgent<AgentState>({
  name: "my_agent",
  initialState: {
    proverbs: [
      "CopilotKit may be new, but its the best thing since sliced bread.",
    ],
  },
})
```

Learn more about shared state
[in the CopilotKit docs](https://docs.copilotkit.ai/adk/shared-state).

### Try it out!

```
npm install && npm run dev
```

## Resources

To see what other features you can build into your UI with AG-UI, refer to the CopilotKit docs:

- [Agentic Generative UI](https://docs.copilotkit.ai/adk/generative-ui/agentic)
- [Human in the Loop](https://docs.copilotkit.ai/adk/human-in-the-loop/agent)
- [Frontend Actions](https://docs.copilotkit.ai/adk/frontend-actions)

Or try them out in the [AG-UI Dojo](https://dojo.ag-ui.com).
