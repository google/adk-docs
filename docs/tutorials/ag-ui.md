# Building in-app agentic chat experiences with ADK and the AG-UI protocol

---

## Overview

As an agent builder, you want your agent to be able to interact with users through a rich and responsive interface. Building that up from scratch will require a lot of effort, especially to support streaming events and client state. That's exactly what AG-UI was designed for, rich user experiences directly connected to an agent.

AG-UI provides a consistent interface to empower rich clients across technology stacks, from mobile to the web and even the command line. There are a number of clients that support AG-UI
<ul>
  <li><a href="https://copilotkit.ai">CopilotKit</a> provides react tooling and components to tightly integrate your agent with web applications</li>
  <li>A <a href="https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/kotlin">Kotlin</a> client</li>
  <li>A <a href="https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/java">Java</a> client</li>
  <li>A <a href="https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/go/example/client">Go</a> client</li>
  <li>Even direct <a href="https://github.com/ag-ui-protocol/ag-ui/tree/main/apps/client-cli-example/src">CLI</a> implementations in typescript</li>
  <li>More on the way from the community, like Rust and Angular.</li>
</ul>

This tutorial uses CopilotKit to create a sample application demoing some of the features supported by AG-UI

<video
  src="https://cdn.copilotkit.ai/docs/copilotkit/images/coagents/chat-example.mp4"
  className="rounded-lg shadow-xl"
  loop
  playsInline
  controls
  autoPlay
  muted
  style="max-width:min(100%, 1024px); display:block; margin-left: auto; margin-right: auto;"
/>

---

## Quickstart

To get started, let's create a sample application with an ADK agent and simple web client

```
npx create-ag-ui-app@latest --adk
```

Let's see what UI features this agent is empowered with:

---

### Chat

Chat is a familiar interface for exposing your agent, and AG-UI handles streaming messages between your users and agents.

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

See more [in the docs](https://docs.copilotkit.ai/adk/agentic-chat-ui)


### Tool Based Generative UI (Rendering Tools)

AG-UI lets you share tool information with your UI so that it can be displayed for users. We call this Generative UI.

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

See more [in the docs](https://docs.copilotkit.ai/adk/generative-ui/tool-based)


### Shared State

ADK agents are stateful, and synchronizing that state between your agents and your UIs enables powerful and fluid user experiences. State can be synchronized both ways
so agents are automatically aware of changes made by your user or other parts of your application.
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
See more [in the docs](https://docs.copilotkit.ai/adk/shared-state)

### Try it out!

```
npm install && npm run dev
```

---

## Resources

To see what other features you can build into your UI with AG-UI, take a look at the docs:
<ul>
  <li><a href="https://docs.copilotkit.ai/adk/generative-ui/agentic">Agentic Generative UI</a></li>
  <li><a href="https://docs.copilotkit.ai/adk/human-in-the-loop/agent">Human in the Loop</a></li>
  <li><a href="https://docs.copilotkit.ai/adk/frontend-actions">Frontend Actions</a></li>
</ul>

Or try them out in the [AG-UI Dojo](https://dojo.ag-ui.com)
