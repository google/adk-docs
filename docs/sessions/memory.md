# Memory: Long-term knowledge with `MemoryService`

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

While a `Session` tracks the history (`events`) and temporary data (`state`) of
a single conversation, an agent may need to recall information from past
interactions. This is where the concept of **Long-Term Knowledge** and the
**`MemoryService`** come into play. Think of it this way:

- **`Session` / `State`:** It's your short-term memory during one specific chat.
- **Long-Term Knowledge (`MemoryService`)**: It's a searchable archive or
  knowledge library the agent can consult, potentially containing information
  from many past chats or other sources.

## The `MemoryService` role

The `BaseMemoryService` (or `Service` in Go) defines the interface for managing
this searchable, long-term knowledge store. It supports these operations:

- **Ingesting Information:**
    - **`add_session_to_memory`**: Takes a completed `Session` and adds relevant
      information to the long-term knowledge store. This approach is ideal for
      automatically capturing the essence of a conversation.
    - **`add_events_to_memory`**: Appends a delta of events (for example, the
      latest turn) without re-ingesting the full session. Useful when you want
      to write to memory partway through a long-running session.
    - **`add_memory`**: Adds explicit `MemoryEntry` objects directly to the
      memory. This method gives you fine-grained control and is useful for
      injecting specific facts from other sources.
- **Searching Information (`search_memory`):** Lets an agent (typically via a
  `Tool`) query the knowledge store and retrieve relevant snippets or context
  based on a search query.

`add_events_to_memory` and `add_memory` are optional and are not implemented by
every service, so confirm that your chosen service supports them before relying
on them.

## Choose the right memory service

The Python ADK ships three `MemoryService` implementations. Use the table below
to decide which is the best fit for your agent.

| **Feature** | **InMemoryMemoryService** | **VertexAiMemoryBankService** | **VertexAiRagMemoryService** |
| :--- | :--- | :--- | :--- |
| **Persistence** | None, data is lost on restart | Yes, managed by the Agent Platform | Yes, stored in Knowledge Engine |
| **Primary Use Case** | Prototyping, local development, and simple testing. | Building meaningful, evolving memories from user conversations. | Vector-search retrieval over the full conversation corpus, or alongside other RAG-indexed content. |
| **Memory Extraction** | Stores full conversation | Extracts [meaningful information](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/generate-memories) from conversations and consolidates it with existing memories powered by LLM | Stores full conversation, indexed by [Knowledge Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-overview). |
| **Search Capability** | Basic keyword matching. | Advanced semantic search. | Vector similarity search over Knowledge Engine. |
| **Setup Complexity** | None. It's the default. | Low. Requires an [Agent Runtime](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview) instance on Agent Platform. | Medium. Requires [Knowledge Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/manage-your-rag-corpus). |
| **Dependencies** | None. | Google Cloud Project, Agent Platform API | Google Cloud Project, Knowledge Engine, the Agent Platform SDK (optional install). |
| **When to use it** | When you want to search across multiple sessions’ chat histories for prototyping. | When you want your agent to remember and learn from past interactions. | When you already have RAG infrastructure or want to retrieve over raw conversation transcripts. |

`VertexAiRagMemoryService` is only exported from `google.adk.memory` when the
Agent Platform SDK is installed. Memory Bank and RAG-backed memory are
documented in [Memory Bank](#memory-bank) and [RAG Memory](#rag-memory) below.


## `InMemoryMemoryService`

The `InMemoryMemoryService` stores session information in the application's
memory and performs basic keyword matching for searches. It requires no setup
and is best for prototyping and simple testing scenarios where persistence isn't
required.

=== "Python"

    ```py
    from google.adk.memory import InMemoryMemoryService
    memory_service = InMemoryMemoryService()
    ```

=== "TypeScript"

    ```typescript
    import { InMemoryMemoryService } from '@google/adk';
    const memoryService = new InMemoryMemoryService();
    ```

=== "Go"

    ```go
    import (
      "google.golang.org/adk/v2/memory"
      "google.golang.org/adk/v2/session"
    )

    // Services must be shared across runners to share state and memory.
    sessionService := session.InMemoryService()
    memoryService := memory.InMemoryService()
    ```

=== "Java"

    ```java
    import com.google.adk.memory.InMemoryMemoryService;

    InMemoryMemoryService memoryService = new InMemoryMemoryService();
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/sessions/MemoryExample.kt:instantiate_service"
    ```

**Example: Add and search memory**

This example demonstrates the basic flow using the `InMemoryMemoryService` for
simplicity.

=== "Python"

    ```py
    import asyncio
    from google.adk.agents import LlmAgent
    from google.adk.sessions import InMemorySessionService, Session
    from google.adk.memory import InMemoryMemoryService # Import MemoryService
    from google.adk.runners import Runner
    from google.adk.tools import load_memory # Tool to query memory
    from google.genai.types import Content, Part

    # --- Constants ---
    APP_NAME = "memory_example_app"
    USER_ID = "mem_user"
    MODEL = "gemini-flash-latest" # Use a valid model

    # --- Agent Definitions ---
    # Agent 1: Simple agent to capture information
    info_capture_agent = LlmAgent(
        model=MODEL,
        name="InfoCaptureAgent",
        instruction="Acknowledge the user's statement.",
    )

    # Agent 2: Agent that can use memory
    memory_recall_agent = LlmAgent(
        model=MODEL,
        name="MemoryRecallAgent",
        instruction="Answer the user's question. Use the 'load_memory' tool "
                    "if the answer might be in past conversations.",
        tools=[load_memory] # Give the agent the tool
    )

    # --- Services ---
    # Services must be shared across runners to share state and memory
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService() # Use in-memory for demo

    async def run_scenario():
        # --- Scenario ---

        # Turn 1: Capture some information in a session
        print("--- Turn 1: Capturing Information ---")
        runner1 = Runner(
            # Start with the info capture agent
            agent=info_capture_agent,
            app_name=APP_NAME,
            session_service=session_service,
            memory_service=memory_service # Provide the memory service to the Runner
        )
        session1_id = "session_info"
        await runner1.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session1_id)
        user_input1 = Content(parts=[Part(text="My favorite project is Project Alpha.")], role="user")

        # Run the agent
        final_response_text = "(No final response)"
        async for event in runner1.run_async(user_id=USER_ID, session_id=session1_id, new_message=user_input1):
            if event.is_final_response() and event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
        print(f"Agent 1 Response: {final_response_text}")

        # Get the completed session
        completed_session1 = await runner1.session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session1_id)

        # Add this session's content to the Memory Service
        print("\n--- Adding Session 1 to Memory ---")
        await memory_service.add_session_to_memory(completed_session1)
        print("Session added to memory.")

        # Turn 2: Recall the information in a new session
        print("\n--- Turn 2: Recalling Information ---")
        runner2 = Runner(
            # Use the second agent, which has the memory tool
            agent=memory_recall_agent,
            app_name=APP_NAME,
            session_service=session_service, # Reuse the same service
            memory_service=memory_service   # Reuse the same service
        )
        session2_id = "session_recall"
        await runner2.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session2_id)
        user_input2 = Content(parts=[Part(text="What is my favorite project?")], role="user")

        # Run the second agent
        final_response_text_2 = "(No final response)"
        async for event in runner2.run_async(user_id=USER_ID, session_id=session2_id, new_message=user_input2):
            if event.is_final_response() and event.content and event.content.parts:
                final_response_text_2 = event.content.parts[0].text
        print(f"Agent 2 Response: {final_response_text_2}")

    # To run this example, you can use the following snippet:
    # asyncio.run(run_scenario())

    # await run_scenario()
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/sessions/memory_example.ts:full_example"
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/sessions/memory_example/memory_example.go:full_example"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/sessions/MemoryExample.java:full_example"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/sessions/MemoryExample.kt:full_example"
    ```

### Search memory within a tool

You can also search memory from within a custom tool by using the tool context.

=== "Python"

    ```python
    from google.adk.tools import ToolContext

    async def search_past_conversations(
        query: str, tool_context: ToolContext
    ) -> dict:
        response = await tool_context.search_memory(query)
        return {
            "results": [
                part.text
                for entry in response.memories
                for part in (entry.content.parts or [])
                if part.text
            ]
        }
    ```

=== "TypeScript"

    ```typescript
    // Within a tool implementation
    async runAsync({ args, toolContext }: RunAsyncToolRequest) {
      const query = args['query'] as string;
      const response = await toolContext.searchMemory(query);
      // process response
      return {
        memories: response.memories.map(m => m.content.parts?.map(p => p.text).join(' ')).join('\n')
      };
    }
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/sessions/memory_example/memory_example.go:tool_search"
    ```

=== "Java"

    ```java
    // Within a tool implementation
    public Single<ToolOutput> execute(ToolContext context) {
      String query = ...; // get query from arguments
      return context.searchMemory(query)
          .map(response -> {
              // process response
              return new ToolOutput(response.memories().toString());
          });
    }
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/sessions/MemoryExample.kt:search_within_tool"
    ```

## Memory Bank

The `VertexAiMemoryBankService` connects your agent to [Memory
Bank](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview),
a fully managed Google Cloud service that provides sophisticated, persistent
memory capabilities for conversational agents.

### How it works

The service handles two key operations:

- **Generating Memories:** At the end of a conversation, you can send the
  session's events to the Memory Bank, which intelligently processes and stores
  the information as "memories."
- **Retrieving Memories:** Your agent code can issue a search query against the
  Memory Bank to retrieve relevant memories from past conversations.

### Direct memory ingestion with `add_memory`

Besides generating memories from session history, `VertexAiMemoryBankService`
also supports direct memory ingestion via the `add_memory` method. This method
gives you precise control over the facts stored in the Memory Bank.

How it works depends on the `enable_consolidation` option:

- **Direct Creation (Default):** By default, `add_memory` calls the underlying
  `memories.create` API. Each `MemoryEntry` you provide is added as a distinct,
  separate memory item.

    ```python
    from google.adk.memory import VertexAiMemoryBankService
    from google.adk.memory.memory_entry import MemoryEntry
    from google.genai.types import Content, Part

    memory_service = VertexAiMemoryBankService(...)

    await memory_service.add_memory(
        app_name="my-app",
        user_id="user-123",
        memories=[
            MemoryEntry(content=Content(parts=[Part(text="The user's favorite color is blue.")]))
        ]
    )
    ```

- **Creation with Consolidation:** If you set `enable_consolidation` to `True`
  in the `custom_metadata`, the service uses the `memories.generate` API. This
  setting allows the Memory Bank to intelligently consolidate the new memory
  items with existing related memories, preventing redundancy and building a
  more coherent knowledge base.

    ```python
    await memory_service.add_memory(
        app_name="my-app",
        user_id="user-123",
        memories=[
            MemoryEntry(content=Content(parts=[Part(text="The user's favorite color is light blue.")]))
        ],
        custom_metadata={"enable_consolidation": True}
    )
    ```

### Prerequisites

Before you can use this feature, you must have:

1. **A Google Cloud Project:** With the Agent Platform API enabled.
2. **An Agent Runtime:** You need to create an Agent Runtime on Agent Platform.
   You do not need to deploy your agent to Agent Runtime to use Memory Bank.
   This setup will provide you with the **Agent Runtime ID** required for
   configuration.
3. **Authentication:** Ensure your local environment is authenticated to access
   Google Cloud services. The simplest way is to run:

    ```bash
    gcloud auth application-default login
    ```

4. **Environment Variables:** The service requires your Google Cloud Project ID
   and Location. Set them as environment variables:

    ```bash
    export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
    export GOOGLE_CLOUD_LOCATION="your-gcp-location"
    ```

For more information on connecting to Google Cloud from ADK agents, see [Connect
to Google Cloud and Agent Platform](/get-started/google-cloud/).

### Configuration

To connect your agent to the Memory Bank, you use the `--memory_service_uri`
flag when starting the ADK server (`adk web` or `adk api_server`). The Uniform
Resource Identifier (URI) must be in the format
`agentengine://<agent_engine_id>`.

```bash title="bash"
adk web path/to/your/agents_dir --memory_service_uri="agentengine://1234567890"
```

Or, you can configure your agent to use the Memory Bank by manually
instantiating the `VertexAiMemoryBankService` and passing it to the `Runner`.

=== "Python"

    ```py
    from google import adk
    from google.adk.memory import VertexAiMemoryBankService

    memory_service = VertexAiMemoryBankService(
        project="PROJECT_ID",
        location="LOCATION",
        agent_engine_id="AGENT_ENGINE_ID"
    )

    runner = adk.Runner(
        ...
        memory_service=memory_service
    )
    ```

## RAG memory

The `VertexAiRagMemoryService` stores conversations in [Knowledge
Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-overview)
and retrieves them by vector similarity. Use it when you already have RAG
infrastructure or want raw transcript retrieval rather than the LLM-extracted
memories produced by Memory Bank. Requires the Agent Platform SDK.

=== "Python"

    ```py
    from google.adk.memory import VertexAiRagMemoryService

    memory_service = VertexAiRagMemoryService(
        rag_corpus="projects/PROJECT_ID/locations/LOCATION/ragCorpora/CORPUS_ID",
        similarity_top_k=5,
        vector_distance_threshold=0.6,
    )
    ```

## Use memory in your agent

When a memory service is configured, your agent can use a tool or callback to
retrieve memories. ADK includes two pre-built tools for retrieving memories:

- **Preload memory**: Automatically retrieves memory at the beginning of each
  turn, similar to a callback.
- **Load memory**: Retrieves memory when your agent decides it would be helpful.

**Example:**

=== "Python"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools import preload_memory

    agent = Agent(
        model=MODEL_ID,
        name='weather_sentiment_agent',
        instruction="...",
        tools=[preload_memory]
    )
    ```

=== "TypeScript"

    ```typescript
    import { LlmAgent, PRELOAD_MEMORY } from '@google/adk';

    const agent = new LlmAgent({
        model: MODEL_ID,
        name: 'weather_sentiment_agent',
        instruction: "...",
        tools: [PRELOAD_MEMORY]
    });
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/v2/agent/llmagent"
        "google.golang.org/adk/v2/tool"
        "google.golang.org/adk/v2/tool/preloadmemorytool"
    )

    agent, _ := llmagent.New(llmagent.Config{
        Model:       model,
        Name:        "weather_sentiment_agent",
        Instruction: "...",
        Tools:       []tool.Tool{preloadmemorytool.New()},
    })
    ```

=== "Java"

    ```java
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.tools.LoadMemoryTool;

    LlmAgent agent = new LlmAgent.Builder()
        .model(MODEL_ID)
        .name("weather_sentiment_agent")
        .instruction("...")
        .tools(new LoadMemoryTool())
        .build();
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/sessions/MemoryExample.kt:preload_memory_agent"
    ```

To extract memories from your session, you need to call `add_session_to_memory`.
For example, you can automate this step with a callback:

=== "Python"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools import preload_memory

    async def auto_save_session_to_memory_callback(callback_context):
        await callback_context.add_session_to_memory()

    agent = Agent(
        model=MODEL,
        name="Generic_QA_Agent",
        instruction="Answer the user's questions",
        tools=[preload_memory],
        after_agent_callback=auto_save_session_to_memory_callback,
    )
    ```

=== "TypeScript"

    ```typescript
    import { LlmAgent, PRELOAD_MEMORY, SingleAgentCallback } from '@google/adk';

    const autoSaveSessionToMemoryCallback: SingleAgentCallback = async (callbackContext) => {
        if (callbackContext.invocationContext.memoryService) {
            await callbackContext.invocationContext.memoryService.addSessionToMemory(
                callbackContext.invocationContext.session
            );
        }
    };

    const agent = new LlmAgent({
        model: MODEL,
        name: "Generic_QA_Agent",
        instruction: "Answer the user's questions",
        tools: [PRELOAD_MEMORY],
        afterAgentCallback: autoSaveSessionToMemoryCallback,
    });
    ```

=== "Go"

    ```go
    import (
        "context"
        "google.golang.org/adk/v2/agent"
        "google.golang.org/adk/v2/agent/llmagent"
        "google.golang.org/adk/v2/session"
        "google.golang.org/adk/v2/tool"
        "google.golang.org/adk/v2/tool/loadmemorytool"
    )

    func autoSaveSessionToMemoryCallback(ctx agent.CallbackContext, s session.Session) (*genai.Content, error) {
        if err := ctx.Memory().AddSessionToMemory(context.Background(), s); err != nil {
            return nil, err
        }
        return nil, nil
    }

    agent, _ := llmagent.New(llmagent.Config{
        Model:               model,
        Name:                "Generic_QA_Agent",
        Instruction:         "Answer the user's questions",
        Tools:               []tool.Tool{loadmemorytool.New()},
        AfterAgentCallbacks: []agent.AfterAgentCallback{autoSaveSessionToMemoryCallback},
    })
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/sessions/MemoryExample.kt:auto_save_callback"
    ```

## Extend memory capabilities

Memory services extended from `BaseMemoryService` support adding sessions and
events to agent memory, including custom metadata. Use the
`add_session_to_memory` and `add_events_to_memory` methods of memory services
such as `InMemoryMemoryService` to amend memory data, as shown in the
following code example:

```python
import asyncio
from google.adk.memory import InMemoryMemoryService

# Assume my_memory_service is an instance of InMemoryMemoryService
# and my_latest_events is a list of new adk.Event objects from the latest turn.
my_latest_events = [...]

async def update_incremental_memory(my_memory_service, my_latest_events):
    # Example 1: Basic incremental update
    await my_memory_service.add_events_to_memory(
        app_name="my-app",
        user_id="my-user",
        events=my_latest_events,
        session_id="my-optional-session-id"
    )

    # Example 2: Incremental update with Custom Metadata
    await my_memory_service.add_events_to_memory(
        app_name="my-app",
        user_id="my-user",
        events=my_latest_events,
        session_id="my-optional-session-id",
        custom_metadata={
            "my_custom_key": "my_custom_value"
        }
    )

async def update_session_memory(my_memory_service, my_completed_session):
    # Example 3: Applying custom metadata to a full session
    await my_memory_service.add_session_to_memory(
        session=my_completed_session,
        custom_metadata={
            "category": "user_preference"
        }
    )

```

## Advanced concepts

### How memory works in practice

The memory workflow includes the following steps:

1. **Session Interaction:** A user interacts with an agent via a `Session`,
   managed by a `SessionService`. During this interaction, events are recorded
   and session state may be updated.
2. **Ingestion into Memory:** When a session concludes or captures significant
   information, your application calls
   `memory_service.add_session_to_memory(session)`. This action extracts key
   data and persists it to your long-term knowledge store, such as the Agent
   Runtime Memory Bank.
3. **Later Query:** In a different, or in the same session, you might ask a
   question requiring past context, for example, "What did we discuss about
   project X last week?".
4. **Agent Uses Memory Tool:** An agent equipped with a memory-retrieval tool,
   such as the built-in `load_memory` tool, recognizes the need for past
   context. It calls the tool, providing a search query (e.g., "discussion
   project X last week").
5. **Search Execution:** The tool internally calls
   `memory_service.search_memory(app_name=..., user_id=..., query=...)`.
6. **Results Returned:** The `MemoryService` searches its store, using keyword
   matching or semantic search, and returns matching snippets as a
   `SearchMemoryResponse` containing a list of `MemoryEntry` objects, each
   holding `content`, and all optional: `author`, `timestamp`, and
   `custom_metadata`.
7. **Agent Uses Results:** The tool returns these results to the agent, usually
   as part of the context or function response. The agent can then use this
   retrieved information to formulate its final answer to the user.

### Can an agent have access to more than one memory service?

- **Through Standard Configuration: No.** The framework (`adk web`, `adk
  api_server`) is designed to be configured with one memory service at a time
  via the `--memory_service_uri` flag. That single service is wired into the
  runner and exposed through `tool_context.search_memory()` and
  `callback_context.search_memory()`.
- **Within Your Agent's Code: Yes.** You can instantiate a second
  `BaseMemoryService` and consult it from a custom tool, which already has a
  `ToolContext` for the framework-configured service.

For example, your agent can use the framework-configured `InMemoryMemoryService`
for conversation history and manually instantiate a second service, a
`VertexAiMemoryBankService`, a `VertexAiRagMemoryService` over a docs corpus, or
any other `BaseMemoryService` implementation, for a separate knowledge base.

#### Example: Use two memory services

=== "Python"

    ```python
    from google.adk.agents import Agent
    from google.adk.memory import InMemoryMemoryService
    from google.adk.tools import ToolContext

    # Second memory service for docs lookup; could be any BaseMemoryService.
    docs_memory = InMemoryMemoryService()


    async def search_all_memory(query: str, tool_context: ToolContext) -> dict:
        """Search both the conversational memory and the docs corpus."""
        conversational = await tool_context.search_memory(query)
        docs = await docs_memory.search_memory(
            app_name="docs", user_id="shared", query=query
        )
        return {
            "from_conversations": [
                part.text
                for entry in conversational.memories
                for part in (entry.content.parts or [])
                if part.text
            ],
            "from_docs": [
                part.text
                for entry in docs.memories
                for part in (entry.content.parts or [])
                if part.text
            ],
        }


    agent = Agent(
        model="gemini-flash-latest",
        name="multi_memory_agent",
        instruction=(
            "Answer questions using both your conversation history and the "
            "docs knowledge base. Use the search_all_memory tool."
        ),
        tools=[search_all_memory],
    )
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/sessions/MemoryExample.kt:multi_memory"
    ```
