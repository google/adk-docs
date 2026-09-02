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

You can always import `VertexAiRagMemoryService` from `google.adk.memory`, but
constructing it raises `ImportError` unless the Agent Platform SDK is installed
with `pip install google-adk[gcp]`. Memory Bank and RAG-backed memory are
documented in [Memory Bank](#memory-bank) and [RAG Memory](#rag-memory) below.


## `InMemoryMemoryService`

The `InMemoryMemoryService` stores session information in the application's
memory and performs basic keyword matching for searches. It requires no setup
and is best for prototyping and simple testing scenarios where persistence isn't
required.

=== "Python"

    ```py
    --8<-- "examples/inline/python/sessions/memory/001-inmemorymemoryservice.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/sessions/memory/002-inmemorymemoryservice.ts"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/sessions/memory/003-inmemorymemoryservice.go.txt"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/sessions/memory/004-inmemorymemoryservice.java"
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
    --8<-- "examples/inline/python/sessions/memory/005-inmemorymemoryservice.py"
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
    --8<-- "examples/inline/python/sessions/memory/006-search-memory-within-a-tool.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/sessions/memory/007-search-memory-within-a-tool.ts"
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/sessions/memory_example/memory_example.go:tool_search"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/sessions/memory/008-search-memory-within-a-tool.java"
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
    --8<-- "examples/inline/python/sessions/memory/009-direct-memory-ingestion-with-addmemory.py"
    ```

- **Creation with Consolidation:** If you set `enable_consolidation` to `True`
  in the `custom_metadata`, the service uses the `memories.generate` API. This
  setting allows the Memory Bank to intelligently consolidate the new memory
  items with existing related memories, preventing redundancy and building a
  more coherent knowledge base.

    ```python
    --8<-- "examples/inline/python/sessions/memory/010-direct-memory-ingestion-with-addmemory.py"
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
    --8<-- "examples/inline/python/sessions/memory/011-configuration.py"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/sessions/MemoryExample.kt:memory_bank"
    ```

## RAG memory

The `VertexAiRagMemoryService` stores conversations in [Knowledge
Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-overview)
and retrieves them by vector similarity. Use it when you already have RAG
infrastructure or want raw transcript retrieval rather than the LLM-extracted
memories produced by Memory Bank. Requires the Agent Platform SDK.

=== "Python"

    ```py
    --8<-- "examples/inline/python/sessions/memory/012-rag-memory.py"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/sessions/MemoryExample.kt:rag_memory"
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
    --8<-- "examples/inline/python/sessions/memory/013-use-memory-in-your-agent.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/sessions/memory/014-use-memory-in-your-agent.ts"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/sessions/memory/015-use-memory-in-your-agent.go.txt"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/sessions/memory/016-use-memory-in-your-agent.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/sessions/MemoryExample.kt:preload_memory_agent"
    ```

To extract memories from your session, you need to call `add_session_to_memory`.
For example, you can automate this step with a callback:

=== "Python"

    ```python
    --8<-- "examples/inline/python/sessions/memory/017-use-memory-in-your-agent.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/sessions/memory/018-use-memory-in-your-agent.ts"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/sessions/memory/019-use-memory-in-your-agent.go.txt"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/sessions/MemoryExample.kt:auto_save_callback"
    ```

### Write specific events or facts from a callback

<div class="language-support-tag">
   <span class="lst-supported">Supported in ADK</span><span class="lst-kotlin">Kotlin v0.7.0</span>
</div>

The `CallbackContext.addSessionToMemory` method is the default behavior for
memory and saves the whole session of your agent. When you want finer control,
`CallbackContext` also offers two more methods: `addEventsToMemory`, for a
chosen subset of events, and `addMemory`, for facts you construct yourself.
Both accept optional `customMetadata`, and both fill in the app, user and
session from the current invocation.

```kotlin
--8<-- "examples/kotlin/snippets/sessions/MemoryExample.kt:callback_memory_writes"
```

All three throw `IllegalStateException` if the runner has no memory service
configured, so they fail at run time rather than at compile time.

## Extend memory capabilities

Memory services extended from `BaseMemoryService` support adding sessions and
events to agent memory, including custom metadata. Use the
`add_session_to_memory` and `add_events_to_memory` methods of memory services
such as `InMemoryMemoryService` to amend memory data, as shown in the
following code example:

```python
--8<-- "examples/inline/python/sessions/memory/020-extend-memory-capabilities.py"
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
   holding `content`, and all optional: `id`, `author`, `timestamp`, and
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
    --8<-- "examples/inline/python/sessions/memory/021-example-use-two-memory-services.py"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/sessions/MemoryExample.kt:multi_memory"
    ```
