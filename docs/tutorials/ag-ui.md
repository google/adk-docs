# Building in-app agentic chat experiences with ADK and the AG-UI protocol

---

## Background

ADK is compatible with AG-UI -- the [Agent-User Interaction Protocol](https://ag-ui.com/introduction) -- and can be used to power fully-featured agentic chat and in-app experiences.

This guide showcases how to bring ADK agents into applications through AG-UI and CopilotKit.


<video
  src="https://cdn.copilotkit.ai/docs/copilotkit/images/coagents/chat-example.mp4"
  className="rounded-lg shadow-xl"
  loop
  playsInline
  controls
  autoPlay
  muted
  style="max-width:min(100%, 1024px);:1024px; display:block; margin-left: auto; margin-right: auto;"
/>

---

## Quickstart

To get started, let's create a sample application with an ADK agent and simple web client

```
npx create-ag-ui-app@latest --adk
```

We will be rebuilding the page and agent to demonstrate several features individually, but this will provide you with an agent
and application that already demonstrates several of the features together.

---

## Styling and Customization

You can

- [Style the copilot UI with CSS, custom icons, and custom labels](https://docs.copilotkit.ai/adk/custom-look-and-feel/customize-built-in-ui-components)
- [Provide custom sub-components](https://docs.copilotkit.ai/adk/custom-look-and-feel/bring-your-own-components)
- And [use fully headless UI](https://docs.copilotkit.ai/adk/custom-look-and-feel/headless-ui) for full programmatic control

---

## Chat with an agent

<video
  src="https://cdn.copilotkit.ai/docs/copilotkit/images/coagents/agentic-chat-ui.mp4"
  className="rounded-lg shadow-xl"
  loop
  playsInline
  controls
  autoPlay
  muted
  style="max-width:min(100%, 1024px);:1024px; display:block; margin-left: auto; margin-right: auto;"
/>

### What is this?

Agentic chat UIs are ways for your users to interact with your agent. In this demo, we use the `CopilotSidebar` component from CopilotKit's
react client to provide collapsible and expandable sidebar chat interface.

### Implementation

If you've followed the quickstart above _you already have a agentic chat UI setup_! Nothing else is needed to get started.

```tsx title="src/app/page.tsx"
<CopilotSidebar
  clickOutsideToClose={false}
  defaultOpen={true}
  labels={{
    title: "Popup Assistant",
    initial: "👋 Hi, there! You're chatting with an agent. This agent comes with a few tools to get you started.\n\nFor example you can try:\n- **Frontend Tools**: \"Set the theme to orange\"\n- **Shared State**: \"Write a proverb about AI\"\n- **Generative UI**: \"Get the weather in SF\"\n\nAs you interact with the agent, you'll see the UI update in real-time to reflect the agent's **state**, **tool calls**, and **progress**."
  }}
/>
```

---

## Agentic Generative UI

<video
  src="https://cdn.copilotkit.ai/docs/copilotkit/images/coagents/agentic-generative-ui.mp4"
  className="rounded-lg shadow-xl"
  loop
  playsInline
  controls
  autoPlay
  muted
  style="max-width:min(100%, 1024px);:1024px; display:block; margin-left: auto; margin-right: auto;"
/>

### What is this?

All ADK agents are stateful. This means that as your agent progresses through nodes, a state object is passed between them preserving the overall state of a session. AG-UI allows you to render this state in your application with custom UI components, which we call _Agentic Generative UI_.

### When should I use this?

Rendering the state of your agent in the UI is useful when you want to provide the user with feedback about the overall state of a session. A great example of this
is a situation where a user and an agent are working together to solve a problem. The agent can store a draft in its state which is then rendered in the UI.

### Implementation

#### Step 1: Define your agent state

If you're not familiar with ADK, your agents are stateful. As you progress through functions, a state object is updated between them. Through the ag-ui protocol, CopilotKit allows you to easily render this state in your application.

For the sake of this guide, let's say our state looks like this in our agent.

```python title="agent/agent.py"
class SomeAgentState(BaseModel):
  """State for the agent."""

  language: str = "english"
```

#### Step 2: Simulate state updates

Next, let's write some logic into our agent that will simulate state updates occurring.

```python title="agent/agent.py"
import json
from typing import Dict, Optional
from fastapi import FastAPI
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint

# ADK imports
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext
from google.adk.models import LlmResponse, LlmRequest
from google.genai import types

from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class SomeAgentState(BaseModel):
    """State for the agent."""

    language: str = "english"


def set_language(tool_context: ToolContext, new_language: str) -> Dict[str, str]:
    """
    Set the language

    Args:
        "new_language": {
            "type": "string",
            "description": "The language to be saved in state",
        }

    Returns:
        Dict indicating success status and message
    """
    try:
        # Put this into a state object just to confirm the shape
        new_state = {"language": new_language}
        tool_context.state["language"] = new_state["language"]
        return {"status": "success", "message": "language updated successfully"}

    except Exception as e:
        return {"status": "error", "message": f"Error updating language: {str(e)}"}


def on_before_agent(callback_context: CallbackContext):
    """
    Initialize agent state if it doesn't exist.
    """
    if "language" not in callback_context.state:
        # Initialize with default recipe
        default_agent_state = {"language": "english"}
        callback_context.state["language"] = default_agent_state["language"]

    return None


#  modifying the agent's system prompt to include the current state of recipe
def before_model_modifier(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Inspects/modifies the LLM request or skips the call."""
    agent_name = callback_context.agent_name
    if agent_name == "assistant":
        language_json = "No language yet"
        if (
            "language" in callback_context.state
            and callback_context.state["language"] is not None
        ):
            try:
                language_json = json.dumps(callback_context.state["language"], indent=2)
            except Exception as e:
                language_json = f"Error serializing language: {str(e)}"
        # --- Modification Example ---
        # Add a prefix to the system instruction
        original_instruction = llm_request.config.system_instruction or types.Content(
            role="system", parts=[]
        )
        prefix = f"""
You are a helpful assistant
This is the current state of the language choice: {language_json}"""
        # Ensure system_instruction is Content and parts list exists
        if not isinstance(original_instruction, types.Content):
            # Handle case where it might be a string (though config expects Content)
            original_instruction = types.Content(
                role="system", parts=[types.Part(text=str(original_instruction))]
            )
        if not original_instruction.parts:
            original_instruction.parts.append(
                types.Part(text="")
            )  # Add an empty part if none exist

        # Modify the text of the first part
        modified_text = prefix + (original_instruction.parts[0].text or "")
        original_instruction.parts[0].text = modified_text
        llm_request.config.system_instruction = original_instruction

    return None


sample_agent = LlmAgent(
    name="assistant",
    model="gemini-2.5-flash",
    instruction="""
    You are a helpful assistant. Help users by answering their questions and assisting with their needs.
    """,
    tools=[set_language],
    before_agent_callback=on_before_agent,
    before_model_callback=before_model_modifier,
)

# Create ADK middleware agent instance
adk_sample_agent = ADKAgent(
    adk_agent=sample_agent,
    app_name="sample_agent",
    user_id="demo_user",
    session_timeout_seconds=3600,
    use_in_memory_services=True,
)

# Create FastAPI app
app = FastAPI(title="ADK Middleware Agentic Generative UI Sample Agent")

# Add the ADK endpoint
add_adk_fastapi_endpoint(app, adk_sample_agent, path="/")

if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

#### Step 3: Render state of the agent in the chat

Now we can utilize `useCoAgentStateRender` to render the state of our agent _in the chat_.

```tsx title="src/app/page.tsx"
// ...
import { useCoAgent, useCopilotAction, useCoAgentStateRender } from "@copilotkit/react-core";
// ...

// Define the state of the agent, should match the state of the agent in your Flow.
type AgentState = {
  language: string;
};

function YourMainContent({ themeColor }: { themeColor: string }) {
  // styles omitted for brevity
  useCoAgentStateRender<AgentState>({
    name: "my_agent", // the name the agent is served as
    render: ({ state }) => (
      <div className="text-purple-800 text-xl">
        The current language is {state.language || 'not set'}
      </div>
    ),
  });

  return <div>...</div>;
}
```

#### Step 4: Render state outside of the chat

You can also render the state of your agent outside of the chat. This is useful when you want to render the state of your agent anywhere other than the chat.

```tsx title="src/app/page.tsx"
import { useCoAgent } from "@copilotkit/react-core";
// ...

// Define the state of the agent, should match the state of the agent in your Flow.
type AgentState = {
  language: string;
};

function YourMainContent({ themeColor }: { themeColor: string }) {
  // ...

  const { state } = useCoAgent<AgentState>({
    name: "my_agent", // the name the agent is served as
  });

  // ...

  return (
    <div>
      <div className="flex flex-col gap-2 mt-4">
        The current language is {state.language || 'not set'}
      </div>
    </div>
  );
}
```

#### Give it a try!

You've now created a component that will render the agent's state in the chat.

---

## Tool Based Generative UI

<video
  src="https://cdn.copilotkit.ai/docs/copilotkit/images/coagents/tool-based-gen-ui.mp4"
  className="rounded-lg shadow-xl"
  loop
  playsInline
  controls
  autoPlay
  muted
  style="max-width:min(100%, 1024px);:1024px; display:block; margin-left: auto; margin-right: auto;"
/>

### What is this?

Tools are a way for the LLM to call predefined, typically, deterministic functions. CopilotKit allows you to render these tools in the UI
as a custom component, which we call _Generative UI_.

### When should I use this?

Rendering tools in the UI is useful when you want to provide the user with feedback about what your agent is doing, specifically
when your agent is calling tools. CopilotKit allows you to fully customize how these tools are rendered in the chat.

### Implementation

#### Step 1: Give your agent a tool to call

```python title="agent/agent.py"
import uvicorn
from fastapi import FastAPI
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
from google.adk.agents import LlmAgent
import os


def get_weather(location: str = "the entire world") -> str:
    """Get the weather in a given location.

    Args:
        location: The location to get the weather for.

    Returns:
        the weather in the specified location.
    """
    return "it is sunny in " + location


weather_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="weather_agent",
    instruction=f"""
      You are an expert weather analyzer that can tell the current weather in a specific location.
      Use the get_weather tool to get the weather in a specific location. If the user doesn't specify
      a location, use "the entire world" as the location.
      """,
    tools=[get_weather],
)

adk_agent_weather = ADKAgent(
    adk_agent=weather_agent, app_name="weather_demo", user_id="demo_user"
)

# Create FastAPI app
app = FastAPI(title="ADK Middleware Weather Tool Agent")

# Add the ADK endpoint
add_adk_fastapi_endpoint(app, adk_agent_weather, path="/")

port = int(os.getenv("PORT", 8000))
uvicorn.run(app, host="0.0.0.0", port=port)
```

#### Step 2: Render the tool call in your frontend

At this point, your agent will be able to call the `get_weather` tool. Now
we just need to add a `useCopilotAction` hook to render the tool call in the UI.

<Callout type="info" title="Important">
  In order to render a tool call in the UI, the name of the action must match
  the name of the tool.
</Callout>

```tsx title="src/app/page.tsx"
import { useCopilotAction } from "@copilotkit/react-core";
// ...

function YourMainContent({ themeColor }: { themeColor: string }) {
  // ...
  useCopilotAction({
    name: "get_weather",
    available: "frontend", // Mark this as render only
    render: ({ status, args }) => {
      return (
        <p className="text-gray-500 mt-2">
          {status !== "complete" && "Calling weather API..."}
          {status === "complete" &&
            `Called the weather API for ${args.location}.`}
        </p>
      );
    },
  });
  // ...
};
```

#### Give it a try!

Try asking the agent to get the weather for a location. You should see the custom UI component that we added
render the tool call and display the arguments that were passed to the tool.

---

## Human In The Loop

### What is this?

ADK agents are stateful agents that can use tool calls to request user confirmation or input.

CopilotKit lets you to add custom UI to take user input and then pass it back to the agent upon completion.

### Why should I use this?

Human-in-the-loop is a powerful way to implement complex workflows that are production ready. By having a human in the loop,
you can ensure that the agent is always making the right decisions and ultimately is being steered in the right direction.

ADK agents are a great way to implement HITL for more complex workflows where you want to ensure the agent is aware
of everything that has happened during a HITL interaction.

### Implementation

#### Step 1: Add a `useCopilotAction` to your Frontend

First, we'll create a component that renders the agent's essay draft and waits for user approval.
The AG-UI middleware for ADK makes this available to the agent automatically as a tool that it can call to request confirmation.

```tsx title="src/app/page.tsx"
import { useCopilotAction } from "@copilotkit/react-core";
import { Markdown } from "@copilotkit/react-ui";

...

function YourMainContent({ themeColor }: { themeColor: string }) {
  useCopilotAction({
    name: "write_essay",
    available: "enabled",
    description: "Writes an essay and takes the draft as an argument.",
    parameters: [
      {
        name: "draft",
        type: "string",
        description: "The draft of the essay",
        required: true,
      },
    ],
    renderAndWaitForResponse: ({ args, respond, status }) => {
      return (
        <div>
          <div className="text-purple-800">
            <Markdown content={args.draft || 'Preparing your draft...'} />
          </div>
          <div className={`flex gap-4 pt-4 ${status !== "executing" ? "hidden" : ""}`}>
            <button
              onClick={() => respond?.({ accepted: false })}
              disabled={status !== "executing"}
              className="border p-2 rounded-xl w-full text-black"
            >
              Reject Draft
            </button>
            <button
              onClick={() => respond?.({ accepted: true })}
              disabled={status !== "executing"}
              className="bg-blue-500 text-white p-2 rounded-xl w-full"
            >
              Approve Draft
            </button>
          </div>
        </div>
      );
    },
  });

  return <div>...</div>;
}
```

#### Step 2: Set up the ADK Agent

Now we'll setup the ADK agent. The flow is hard to understand without a complete example, so below
is the complete implementation of the agent with explanations.

Some main things to note:

- AG-UI exposes CopilotKit's actions to your agent by binding them as tools.
- If the `writeEssay` action is found in the model's response, the agent will pass control back to the frontend
  to get user feedback.

```python title="agent/agent.py"
import uvicorn
from fastapi import FastAPI
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
from google.adk.agents import LlmAgent
import os

DEFINE_ESSAY_TOOL = """
{
    "type": "function",
    "function": {
        "name": "write_essay",
        "description": "Write an essay from a draft",
        "parameters": {
            "type": "object",
            "properties": {
                "draft": {
                    "type": "string",
                    "description": "The draft of the essay to write"
                }
            },
            "required": ["draft"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "accepted": {
                    "type": "boolean",
                    "description": "if the human approved the draft"
                }
            },
            "required": ["accepted"]
        }
    }
}
"""


sample_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="sample_agent",
    instruction=f"""
    You are a human-in-the-loop essay writing assistant that helps write essays with human oversight and approval.

    **Your Primary Role:**
    - Generate short ~100 word essay drafts for any topic the user requests.
    - Facilitate human review and modification of generated draft
    - When a human approves a draft, return it as text.

    **When a user asks you to write an essay:**
    - ALWAYS come up with a short (roughly 100 word) draft of an essay on the topic.
    - ALWAYS submit the draft to the `write_essay` tool.
    - When the user requests the essay, do not respond with the essay directly before it is approved. Always use the write_essay tool.

    ** PROVIDING THE APPROVED ESSAY TO THE USER: **
    - When the user approves the essay, *ALWAYS* respond with "HERE IS THE ESSAY: <essay>".
    - When the user rejects the essay, *ALWAYS* respond with "REJECTED".

    TOOL_REFERENCE: {DEFINE_ESSAY_TOOL}
    """,
)

adk_sample_agent = ADKAgent(
    adk_agent=sample_agent, app_name="essay_demo", user_id="demo_user"
)

# Create FastAPI app
app = FastAPI(title="ADK Middleware Essay Tool Agent")
# Add the ADK endpoint
add_adk_fastapi_endpoint(app, adk_sample_agent, path="/")

port = int(os.getenv("PORT", 8000))
uvicorn.run(app, host="0.0.0.0", port=port)
```

#### Give it a try!

Try asking your agent to write an essay about the benefits of AI. You'll see that it will generate an essay,
stream the progress and eventually ask you to review it.

---

## Shared State

<video
  src="https://cdn.copilotkit.ai/docs/copilotkit/images/coagents/write-agent-state.mp4"
  className="rounded-lg shadow-xl"
  loop
  playsInline
  controls
  autoPlay
  muted
  style="max-width:min(100%, 1024px);:1024px; display:block; margin-left: auto; margin-right: auto;"
/>

### What is this?

As we saw above in the example explaining Agentic Generative UI you can easily use the realtime agent state not only in the chat UI, but also in the native application UX. This section also shows you how to write to your agent's state from your application.

### When should I use this?

You can use this when you want to provide the user with feedback about your agent's state. As your agent's state updates you can reflect these updates natively in your application. Conversely, as your application's state is updated,
you may want your agent to know about those changes when it's deciding what to do.

### Implementation

#### Step 1: Define the Agent State

As we've already seen, ADK Agents are stateful. As you transition through the flow, that state is updated and available to the next function. For this example,
let's assume that our agent state looks something like this.

```python title="agent/agent.py"
class SomeAgentState(BaseModel):
  """State for the agent."""

  language: str = "english"
```

#### Step 2: Simulate state updates

Next, let's write some logic into our agent that will simulate state updates occurring.

```python title="agent/agent.py"
import json
from typing import Dict, Optional
from fastapi import FastAPI
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint

# ADK imports
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext
from google.adk.models import LlmResponse, LlmRequest
from google.genai import types

from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class SomeAgentState(BaseModel):
    """State for the agent."""

    language: str = "english"


def set_language(tool_context: ToolContext, new_language: str) -> Dict[str, str]:
    """
    Set the language

    Args:
        "new_language": {
            "type": "string",
            "description": "The language to be saved in state",
        }

    Returns:
        Dict indicating success status and message
    """
    try:
        # Put this into a state object just to confirm the shape
        new_state = {"language": new_language}
        tool_context.state["language"] = new_state["language"]
        return {"status": "success", "message": "language updated successfully"}

    except Exception as e:
        return {"status": "error", "message": f"Error updating language: {str(e)}"}


def on_before_agent(callback_context: CallbackContext):
    """
    Initialize agent state if it doesn't exist.
    """
    if "language" not in callback_context.state:
        # Initialize with default recipe
        default_agent_state = {"language": "english"}
        callback_context.state["language"] = default_agent_state["language"]

    return None


# --- Define the Callback Function ---
#  modifying the agent's system prompt to incude the current state of recipe
def before_model_modifier(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Inspects/modifies the LLM request or skips the call."""
    agent_name = callback_context.agent_name
    if agent_name == "assistant":
        language_json = "No language yet"
        if (
            "language" in callback_context.state
            and callback_context.state["language"] is not None
        ):
            try:
                language_json = json.dumps(callback_context.state["language"], indent=2)
            except Exception as e:
                language_json = f"Error serializing language: {str(e)}"
        # --- Modification Example ---
        # Add a prefix to the system instruction
        original_instruction = llm_request.config.system_instruction or types.Content(
            role="system", parts=[]
        )
        prefix = f"""
You are a helpful assistant
This is the current state of the language choice: {language_json}"""
        # Ensure system_instruction is Content and parts list exists
        if not isinstance(original_instruction, types.Content):
            # Handle case where it might be a string (though config expects Content)
            original_instruction = types.Content(
                role="system", parts=[types.Part(text=str(original_instruction))]
            )
        if not original_instruction.parts:
            original_instruction.parts.append(
                types.Part(text="")
            )  # Add an empty part if none exist

        # Modify the text of the first part
        modified_text = prefix + (original_instruction.parts[0].text or "")
        original_instruction.parts[0].text = modified_text
        llm_request.config.system_instruction = original_instruction

    return None


sample_agent = LlmAgent(
    name="assistant",
    model="gemini-2.5-flash",
    instruction="""
    You are a helpful assistant. Help users by answering their questions and assisting with their needs.
    """,
    tools=[set_language],
    before_agent_callback=on_before_agent,
    before_model_callback=before_model_modifier,
)

# Create ADK middleware agent instance
adk_sample_agent = ADKAgent(
    adk_agent=sample_agent,
    app_name="sample_agent",
    user_id="demo_user",
    session_timeout_seconds=3600,
    use_in_memory_services=True,
)

# Create FastAPI app
app = FastAPI(title="ADK Middleware Agentic Generative UI Sample Agent")

# Add the ADK endpoint
add_adk_fastapi_endpoint(app, adk_sample_agent, path="/")

if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

#### Step 3: Use the `useCoAgent` Hook

With your agent connected and running all that is left in order to read the agent state is to call the [useCoAgent](https://docs.copilotkit.ai/reference/hooks/useCoAgent) hook,
pass the agent's name, and optionally provide an initial state.

```tsx title="src/app/page.tsx"
import { useCoAgent } from "@copilotkit/react-core";

// Define the agent state type, should match the actual state of your agent
type AgentState = {
  language: "english" | "spanish";
};

function YourMainContent({ themeColor }: { themeColor: string }) {
  const { state } = useCoAgent<AgentState>({
    name: "my_agent",
    initialState: { language: "spanish" }  // optionally provide an initial state
  });

  // ...

  return (
    // style excluded for brevity
    <div>
      <h1>Your main content</h1>
      <p>Language: {state.language}</p>
    </div>
  );
}
```

_Note:_ The `state` in `useCoAgent` is reactive and will automatically update when the agent's state changes.

#### Step 4: Rendering agent state in the chat

You can also render the agent's state in the chat UI. This is useful for informing the user about the agent's state in a
more in-context way. To do this, you can use the [useCoAgentStateRender](https://docs.copilotkit.ai/reference/hooks/useCoAgentStateRender) hook.

```tsx title="src/app/page.tsx"
import { useCoAgentStateRender } from "@copilotkit/react-core";

// ...

function YourMainContent({ themeColor }: { themeColor: string }) {
  // ...

  useCoAgentStateRender({
    name: "my_agent",
    render: ({ state }) => {
      if (!state.language) return null;
      return (
        <div className="text-purple-800 text-xl">
          The currently selected language is: {state.language}
        </div>
      );
    },
  });

  // ...
}
```

#### Step 5: Call `setState` function from the `useCoAgent` hook

`useCoAgent` returns a `setState` function that you can use to update the agent state. Calling this
will update the agent state and trigger a rerender of anything that depends on the agent state.

```tsx title="src/app/page.tsx"
import { useCoAgent } from "@copilotkit/react-core";

// Example usage in a pseudo React component
function YourMainContent({ themeColor }: { themeColor: string }) {
  const { state, setState } = useCoAgent<AgentState>({
    name: "my_agent",
    initialState: { language: "spanish" }  // optionally provide an initial state
  });

  // ...

  const toggleLanguage = () => {
    setState({ language: state.language === "english" ? "spanish" : "english" });
  };

  // ...

  return (
    // style excluded for brevity
    <div>
      <h1>Your main content</h1>
      <p>Language: {state.language}</p>
      <button onClick={toggleLanguage}>Toggle Language</button>
    </div>
  );
}
```

#### Give it a try!

You can now use the `setState` function to update the agent state and `state` to read it. Try toggling the language using the toggle language
button and try talking to your agent. You'll see the language change to match the agent's state.
