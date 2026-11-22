---
catalog_title: LangGraph
catalog_description: Run compiled state graphs as single-turn or multi-turn ADK agents
catalog_icon: /integrations/assets/adk.png
catalog_tags: ["connectors"]
---

# LangGraph agent for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v2.3.0</span>
</div>

In Agent Development Kit (ADK) Python and ADK TypeScript, the `LangGraphAgent` class adapts a compiled [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) state graph into an ADK `BaseAgent`. You can run existing LangGraph graphs directly inside ADK applications, pass ADK session messages to the graph, and return the graph's final response as an ADK event.

Because `LangGraphAgent` inherits from `BaseAgent`, you can deploy a compiled graph as your standalone root agent, delegate tasks to it as a sub-agent from an ADK orchestrator, or include it inside [ADK workflows](/workflows/).

## Use cases

- **Reuse existing LangGraph graphs**: Run compiled LangGraph workflows inside ADK without rewriting graph nodes, edges, or state reducers.
- **Multi-agent orchestration**: Attach a `LangGraphAgent` as a sub-agent to an ADK `Agent` or workflow agent so ADK handles routing while LangGraph handles specialized graph execution.
- **Stateful multi-turn conversations**: Connect a LangGraph checkpointer to preserve graph state across turns, or let ADK replay conversation history from session events when you do not configure a checkpointer.

## Prerequisites

- Python 3.11 or later for ADK Python, or Node.js 24.13.0 or later for ADK TypeScript.
- A [Gemini API key](https://aistudio.google.com/app/apikey) exported as `GOOGLE_API_KEY`, or credentials for another chat model supported by LangChain.

## Installation

The `LangGraphAgent` class is built into ADK Python and ADK TypeScript. Install the corresponding ADK package together with LangGraph and a LangChain chat model provider package.

=== "Python"

    ```bash
    pip install google-adk "langgraph>=1.0.10,<2" "langgraph-checkpoint>=4.1.1,<5" langchain-google-genai
    ```

    You can also install the LangGraph dependencies through the ADK `extensions` extra with `pip install "google-adk[extensions]"`, along with a chat model provider package such as `langchain-google-genai`. Because LangGraph is an optional dependency in ADK Python, import `LangGraphAgent` directly from `google.adk.agents.langgraph_agent` rather than `google.adk.agents`.

=== "TypeScript"

    ```bash
    npm install @google/adk @langchain/langgraph @langchain/core @langchain/google
    ```

## Use with agent

Build and compile a LangGraph graph whose state includes a `messages` field, then pass the compiled graph to `LangGraphAgent`.

### Basic setup

The following example compiles a single-node LangGraph graph with an in-memory checkpointer and exposes it as an ADK root agent.

=== "Python"

    ```python
    from google.adk.agents.langgraph_agent import LangGraphAgent
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.graph import END, MessagesState, START, StateGraph

    model = ChatGoogleGenerativeAI(model="gemini-flash-latest")


    def assistant_node(state: MessagesState) -> dict:
        response = model.invoke(state["messages"])
        return {"messages": [response]}


    builder = StateGraph(MessagesState)
    builder.add_node("assistant", assistant_node)
    builder.add_edge(START, "assistant")
    builder.add_edge("assistant", END)

    graph = builder.compile(checkpointer=InMemorySaver())

    root_agent = LangGraphAgent(
        name="langgraph_assistant",
        description="Answers user questions using a compiled LangGraph workflow.",
        instruction="You are a helpful assistant.",
        graph=graph,
    )
    ```

=== "TypeScript"

    ```typescript
    import { type CompiledGraphLike, LangGraphAgent } from "@google/adk";
    import { ChatGoogle } from "@langchain/google/node";
    import {
      END,
      MemorySaver,
      MessagesValue,
      START,
      StateGraph,
      StateSchema,
    } from "@langchain/langgraph";

    const State = new StateSchema({
      messages: MessagesValue,
    });

    const model = new ChatGoogle({
      model: "gemini-flash-latest",
    });

    const graph = new StateGraph(State)
      .addNode("assistant", async (state) => {
        const response = await model.invoke(state.messages);
        return { messages: [response] };
      })
      .addEdge(START, "assistant")
      .addEdge("assistant", END)
      .compile({ checkpointer: new MemorySaver() });

    const rootAgent = new LangGraphAgent({
      name: "langgraph_assistant",
      description: "Answers user questions using a compiled LangGraph workflow.",
      instruction: "You are a helpful assistant.",
      // CompiledStateGraph is compatible at runtime, but its generic invoke
      // signature requires a CompiledGraphLike assertion in TypeScript.
      graph: graph as unknown as CompiledGraphLike,
    });

    export { rootAgent };
    ```

### Use as a sub-agent

You can delegate specialized requests to a `LangGraphAgent` from a parent ADK agent. Provide a clear `description` so the parent agent knows when to route requests to the LangGraph sub-agent.

=== "Python"

    ```python
    from google.adk.agents import Agent
    from google.adk.agents.langgraph_agent import LangGraphAgent
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.graph import END, MessagesState, START, StateGraph

    model = ChatGoogleGenerativeAI(model="gemini-flash-latest")


    def draft_node(state: MessagesState) -> dict:
        response = model.invoke(state["messages"])
        return {"messages": [response]}


    builder = StateGraph(MessagesState)
    builder.add_node("draft", draft_node)
    builder.add_edge(START, "draft")
    builder.add_edge("draft", END)

    research_agent = LangGraphAgent(
        name="research_graph_agent",
        description="Synthesizes research notes into structured summaries.",
        instruction="Summarize the user's topic clearly and concisely.",
        graph=builder.compile(checkpointer=InMemorySaver()),
    )

    root_agent = Agent(
        model="gemini-flash-latest",
        name="coordinator_agent",
        instruction=(
            "Route research summary requests to research_graph_agent. "
            "Answer general questions directly."
        ),
        sub_agents=[research_agent],
    )
    ```

=== "TypeScript"

    ```typescript
    import { type CompiledGraphLike, LangGraphAgent, LlmAgent } from "@google/adk";
    import { ChatGoogle } from "@langchain/google/node";
    import {
      END,
      MemorySaver,
      MessagesValue,
      START,
      StateGraph,
      StateSchema,
    } from "@langchain/langgraph";

    const State = new StateSchema({
      messages: MessagesValue,
    });

    const model = new ChatGoogle({
      model: "gemini-flash-latest",
    });

    const researchGraph = new StateGraph(State)
      .addNode("draft", async (state) => {
        const response = await model.invoke(state.messages);
        return { messages: [response] };
      })
      .addEdge(START, "draft")
      .addEdge("draft", END)
      .compile({ checkpointer: new MemorySaver() });

    const researchAgent = new LangGraphAgent({
      name: "research_graph_agent",
      description: "Synthesizes research notes into structured summaries.",
      instruction: "Summarize the user's topic clearly and concisely.",
      graph: researchGraph as unknown as CompiledGraphLike,
    });

    const rootAgent = new LlmAgent({
      model: "gemini-flash-latest",
      name: "coordinator_agent",
      instruction:
        "Route research summary requests to research_graph_agent. " +
        "Answer general questions directly.",
      subAgents: [researchAgent],
    });

    export { rootAgent };
    ```

## How it works

During each turn, `LangGraphAgent` bridges ADK [sessions](/sessions/) and LangGraph graph state in four steps:

1. **Derive the thread ID**: The agent builds a LangGraph runnable configuration with `configurable.thread_id` derived from the active ADK session.
2. **Prepend the system instruction**: If you configured `instruction` and the graph does not already have saved messages for the current thread, the agent prepends a system message with `instruction`. When a checkpointer already stores prior messages for that thread, the agent does not re-send `instruction`.
3. **Select session messages**:
   - **With a checkpointer**: The agent assumes LangGraph persists earlier turns, skips any trailing non-user events, such as a parent coordinator's delegation event, and sends only the most recent contiguous sequence of user messages.
   - **Without a checkpointer**: The agent replays all user messages and all prior responses authored by this `LangGraphAgent` from the ADK session event list. The agent excludes events authored by other agents, such as a parent coordinator.
4. **Invoke the graph and yield an ADK event**: The agent invokes the compiled graph with `{ "messages": messages }` and the runnable configuration, extracts text from the last message in the returned `messages` list, and yields a single ADK `Event` authored by the agent.

### Checkpointers and thread isolation

When you compile a graph with a LangGraph checkpointer, such as `InMemorySaver` or a database-backed checkpointer, ADK maps each session to a LangGraph thread ID:

- **Python**: ADK automatically scopes `configurable.thread_id` to `(app_name, user_id, session_id)` to isolate checkpoint threads across apps and users even when session IDs match.
- **TypeScript**: ADK passes `session.id` directly as `configurable.thread_id`. Ensure your session IDs are unique across users and applications if you share a persistent checkpointer backend.

!!! warning "Persistent checkpointers in Python"

    When you use a persistent LangGraph checkpointer in Python, install `langgraph-checkpoint>=4.1.1`, included in `google-adk[extensions]`, and set `LANGGRAPH_STRICT_MSGPACK=true` in your environment before importing LangGraph and compiling the graph. This environment variable enables LangGraph's strict msgpack deserialization allowlist for saved checkpoints.

## Configuration options

Use the following options when instantiating `LangGraphAgent`. The `LangGraphAgent` class also supports all standard `BaseAgent` options, such as `description`, `sub_agents` or `subAgents`, `before_agent_callback` or `beforeAgentCallback`, and `after_agent_callback` or `afterAgentCallback`.

| Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `name` | `str` / `string` | Required | Unique agent identifier within the agent tree. The agent name cannot be `"user"`. |
| `graph` | `CompiledStateGraph` / `CompiledGraphLike` | Required | Compiled LangGraph graph with a `messages` state key. In TypeScript, assert a `@langchain/langgraph` `CompiledStateGraph` to `CompiledGraphLike`. |
| `instruction` | `str` / `string` | `""` | System instruction prepended as a system message when graph state has no existing messages. |
| `description` | `str` / `string` | `""` | Short summary of the agent's capability, used by parent agents when deciding whether to delegate. |

## Limitations

- **Text-only, non-live execution**: The `LangGraphAgent` class sends only the text of the first part, `parts[0]`, from each ADK session event to the graph and extracts only text content from the final returned message. The agent does not support non-text multimodal parts, such as images or audio, or bidirectional live streaming with `run_live` or `runLive`; non-text inputs can cause validation errors.
- **Single final event per turn**: Intermediate LangGraph node steps and tool calls run inside the graph invocation, and the agent does not stream them as separate ADK events.
- **Non-empty `messages` output required**: The compiled graph must return at least one message in its output `messages` list.

## Additional resources

- [LangGraph Python documentation](https://docs.langchain.com/oss/python/langgraph/overview)
- [LangGraph JavaScript and TypeScript documentation](https://docs.langchain.com/oss/javascript/langgraph/overview)
- [LangGraph persistence and checkpointers (Python)](https://docs.langchain.com/oss/python/langgraph/persistence)
- [LangGraph persistence and checkpointers (TypeScript)](https://docs.langchain.com/oss/javascript/langgraph/persistence)
- [LangGraph on PyPI](https://pypi.org/project/langgraph/)
- [LangGraph on GitHub (Python)](https://github.com/langchain-ai/langgraph)
- [LangGraph.js on GitHub (TypeScript)](https://github.com/langchain-ai/langgraphjs)
- [ADK TypeScript `LangGraphAgent` API reference](/api-reference/typescript/classes/LangGraphAgent.html)
- [ADK Agents overview](/agents/)
