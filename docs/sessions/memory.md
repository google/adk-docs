# Memory: Long-Term Knowledge with `MemoryService`

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

We've seen how `Session` tracks the history (`events`) and temporary data (`state`) for a *single, ongoing conversation*. But what if an agent needs to recall information from *past* conversations? This is where the concept of **Long-Term Knowledge** and the **`MemoryService`** come into play.

Think of it this way:

* **`Session` / `State`:** Like your short-term memory during one specific chat.
* **Long-Term Knowledge (`MemoryService`)**: Like a searchable archive or knowledge library the agent can consult, potentially containing information from many past chats or other sources.

## The `MemoryService` Role

The `BaseMemoryService` defines the interface for managing this searchable, long-term knowledge store. Its primary responsibilities are:

1. **Ingesting Information (`add_session_to_memory`):** Taking the contents of a (usually completed) `Session` and adding relevant information to the long-term knowledge store.
2. **Searching Information (`search_memory`):** Allowing an agent (typically via a `Tool`) to query the knowledge store and retrieve relevant snippets or context based on a search query.

## Choosing the Right Memory Service

The ADK offers three distinct `MemoryService` implementations, each tailored to different use cases. Use the table below to decide which is the best fit for your agent.

| **Feature** | **InMemoryMemoryService** | **VertexAiMemoryBankService** | **OpenMemoryService** |
| :--- | :--- | :--- | :--- |
| **Persistence** | None (data is lost on restart) | Yes (Managed by Vertex AI) | Yes (Self-hosted backend) |
| **Primary Use Case** | Prototyping, local development, and simple testing. | Building meaningful, evolving memories from user conversations. | Self-hosted deployments with data sovereignty requirements, on-premise deployments, cost-effective memory solutions. |
| **Memory Extraction** | Stores full conversation | Extracts [meaningful information](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/generate-memories) from conversations and consolidates it with existing memories (powered by LLM) | Stores session events with multi-sector embeddings and graceful decay |
| **Search Capability** | Basic keyword matching. | Advanced semantic search. | Advanced semantic search with multi-sector embeddings |
| **Setup Complexity** | None. It's the default. | Low. Requires an [Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview) instance in Vertex AI. | Medium. Requires self-hosted OpenMemory backend (Docker or Node.js). |
| **Dependencies** | None. | Google Cloud Project, Vertex AI API | Self-hosted OpenMemory server, `httpx` (via `google-adk[openmemory]`) |
| **When to use it** | When you want to search across multiple sessions' chat histories for prototyping. | When you want your agent to remember and learn from past interactions. | When you need self-hosted, open-source memory with full data control, on-premise deployments, or cost-effective alternatives to cloud services. |

## In-Memory Memory

The `InMemoryMemoryService` stores session information in the application's memory and performs basic keyword matching for searches. It requires no setup and is best for prototyping and simple testing scenarios where persistence isn't required.

=== "Python"

    ```py
    from google.adk.memory import InMemoryMemoryService
    memory_service = InMemoryMemoryService()
    ```

=== "Go"
    ```go
    import (
      "google.golang.org/adk/memory"
      "google.golang.org/adk/session"
    )

    // Services must be shared across runners to share state and memory.
    sessionService := session.InMemoryService()
    memoryService := memory.InMemoryService()
    ```


**Example: Adding and Searching Memory**

This example demonstrates the basic flow using the `InMemoryMemoryService` for simplicity.

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
    MODEL = "gemini-2.0-flash" # Use a valid model

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

=== "Go"

    ```go
    --8<-- "examples/go/snippets/sessions/memory_example/memory_example.go:full_example"
    ```


### Searching Memory Within a Tool

You can also search memory from within a custom tool by using the `tool.Context`.

=== "Go"

    ```go
    --8<-- "examples/go/snippets/sessions/memory_example/memory_example.go:tool_search"
    ```

## Vertex AI Memory Bank

The `VertexAiMemoryBankService` connects your agent to [Vertex AI Memory Bank](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview), a fully managed Google Cloud service that provides sophisticated, persistent memory capabilities for conversational agents.

### How It Works

The service handles two key operations:

*   **Generating Memories:** At the end of a conversation, you can send the session's events to the Memory Bank, which intelligently processes and stores the information as "memories."
*   **Retrieving Memories:** Your agent code can issue a search query against the Memory Bank to retrieve relevant memories from past conversations.

### Prerequisites

Before you can use this feature, you must have:

1.  **A Google Cloud Project:** With the Vertex AI API enabled.
2.  **An Agent Engine:** You need to create an Agent Engine in Vertex AI. You do not need to deploy your agent to Agent Engine Runtime to use Memory Bank. This will provide you with the **Agent Engine ID** required for configuration.
3.  **Authentication:** Ensure your local environment is authenticated to access Google Cloud services. The simplest way is to run:
    ```bash
    gcloud auth application-default login
    ```
4.  **Environment Variables:** The service requires your Google Cloud Project ID and Location. Set them as environment variables:
    ```bash
    export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
    export GOOGLE_CLOUD_LOCATION="your-gcp-location"
    ```

### Configuration

To connect your agent to the Memory Bank, you use the `--memory_service_uri` flag when starting the ADK server (`adk web` or `adk api_server`). The URI must be in the format `agentengine://<agent_engine_id>`.

```bash title="bash"
adk web path/to/your/agents_dir --memory_service_uri="agentengine://1234567890"
```

Or, you can configure your agent to use the Memory Bank by manually instantiating the `VertexAiMemoryBankService` and passing it to the `Runner`.

=== "Python"
  ```py
  from google.adk.memory import VertexAiMemoryBankService

  agent_engine_id = agent_engine.api_resource.name.split("/")[-1]

  memory_service = VertexAiMemoryBankService(
      project="PROJECT_ID",
      location="LOCATION",
      agent_engine_id=agent_engine_id
  )

  runner = adk.Runner(
      ...
      memory_service=memory_service
  )
  ```

## OpenMemory

The `OpenMemoryService` connects your agent to [OpenMemory](https://openmemory.cavira.app/), a self-hosted, open-source memory system that provides brain-inspired multi-sector embeddings, graceful memory decay, and server-side filtering for efficient multi-user agent deployments.

### How It Works

OpenMemory provides a production-ready, self-hosted memory backend that integrates seamlessly with ADK's `BaseMemoryService` interface. The service handles two key operations:

*   **Storing Memories:** Automatically converts ADK session events to OpenMemory memories with enriched content format (embedding author/timestamp metadata).
*   **Retrieving Memories:** Leverages OpenMemory's multi-sector embeddings for semantic search and retrieval, with server-side filtering by `user_id` for multi-tenant isolation.

### Key Features

*   **Multi-sector embeddings:** Factual, emotional, temporal, and relational memory sectors for richer context understanding.
*   **Graceful memory decay:** Automatic reinforcement keeps relevant context sharp while allowing less important memories to fade.
*   **Server-side filtering:** Efficient multi-user isolation through indexed database queries.
*   **Self-hosted:** Full data ownership with no vendor lock-in, perfect for on-premise deployments.
*   **Cost-effective:** 6-10× cheaper than SaaS memory APIs while providing high performance.

### Installation

Install ADK with OpenMemory support:

```bash
pip install google-adk[openmemory]
```

This installs `httpx` for making HTTP requests to the OpenMemory API.

### Prerequisites

Before you can use OpenMemory, you need:

1.  **A self-hosted OpenMemory backend:** You can run OpenMemory using Docker or by setting up the Node.js backend manually. See the [Self-Hosted Setup](#self-hosted-setup) section below.
2.  **Environment Variables (Optional):** You can configure OpenMemory via environment variables or pass them directly to the service:
    ```bash
    export OPENMEMORY_BASE_URL="http://localhost:3000"
    export OPENMEMORY_API_KEY="your-api-key"  # Optional, only if server requires authentication
    ```

### Configuration

You can configure OpenMemory in two ways:

#### Option 1: Using the CLI (Recommended for `adk web` and `adk api_server`)

To connect your agent to OpenMemory using the CLI, use the `--memory_service_uri` flag when starting the ADK server. The URI format is `openmemory://<host>:<port>`.

```bash title="bash"
# Basic usage
adk web path/to/your/agents_dir --memory_service_uri="openmemory://localhost:3000"

# With API key
adk web path/to/your/agents_dir --memory_service_uri="openmemory://localhost:3000?api_key=your-secret-key"

# API server
adk api_server path/to/your/agents_dir --memory_service_uri="openmemory://localhost:3000"
```

**Supported URI formats:**
- `openmemory://localhost:3000` → Connects to `http://localhost:3000`
- `openmemory://localhost:3000?api_key=secret` → Connects with API key authentication
- `openmemory://https://example.com` → Connects to `https://example.com`

#### Option 2: Using Python Code

Alternatively, you can configure OpenMemory by manually instantiating the `OpenMemoryService` and passing it to the `Runner`:

```py
from google.adk.memory import OpenMemoryService
from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService

# Configure OpenMemory with defaults
memory_service = OpenMemoryService(
    base_url="http://localhost:3000",
    api_key="your-key"  # Optional, only if server requires authentication
)

# Create agent
agent = Agent(
    name="my_agent",
    model="gemini-2.0-flash",
    instruction="You are a helpful assistant."
)

# Use with Runner
runner = Runner(
    app_name="my_app",
    agent=agent,
    session_service=InMemorySessionService(),
    artifact_service=InMemoryArtifactService(),
    memory_service=memory_service
)

# Run with memory
response = await runner.run("Hello, remember this conversation!")
```

### Advanced Configuration

You can customize OpenMemory behavior using `OpenMemoryServiceConfig`:

```py
from google.adk.memory import OpenMemoryService, OpenMemoryServiceConfig

# Create custom configuration
config = OpenMemoryServiceConfig(
    search_top_k=20,              # Number of memories to retrieve (default: 10)
    timeout=10.0,                  # Request timeout in seconds (default: 30.0)
    user_content_salience=0.9,    # Importance score for user messages (default: 0.8)
    model_content_salience=0.75,  # Importance score for model responses (default: 0.7)
    default_salience=0.6,         # Fallback salience value (default: 0.6)
    enable_metadata_tags=True      # Toggle session/app tagging (default: True)
)

memory_service = OpenMemoryService(
    base_url="http://localhost:3000",
    api_key="your-api-key",
    config=config
)
```

**Configuration Parameters:**

*   `search_top_k` (int, default: 10): Maximum number of memories to retrieve per search query.
*   `timeout` (float, default: 30.0): HTTP request timeout in seconds.
*   `user_content_salience` (float, default: 0.8): Importance score (0.0-1.0) assigned to user messages when storing memories.
*   `model_content_salience` (float, default: 0.7): Importance score (0.0-1.0) assigned to model responses when storing memories.
*   `default_salience` (float, default: 0.6): Fallback salience value for content without a recognized author.
*   `enable_metadata_tags` (bool, default: True): Whether to include session and app tags for filtering memories by application context.

### Self-Hosted Setup

OpenMemory can be deployed using Docker (recommended) or by setting up the Node.js backend manually.

#### Option 1: Docker (Recommended)

The easiest way to run OpenMemory is using Docker:

```bash
# Run OpenMemory container
docker run -p 3000:3000 cavira/openmemory

# Or use the production network build
docker run -p 3000:3000 cavira/openmemory:production
```

Verify it's running:

```bash
curl http://localhost:3000/health
```

#### Option 2: Node.js Backend

For more control, you can set up the OpenMemory backend manually:

1.  **Clone the OpenMemory repository:**
    ```bash
    git clone https://github.com/CaviraOSS/OpenMemory.git
    cd OpenMemory/backend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Configure environment variables:**
    
    Create a `.env` file in `OpenMemory/backend/`:
    ```bash
    # Embedding Provider (e.g., Gemini)
    OM_EMBEDDINGS=gemini
    GEMINI_API_KEY=your-gemini-api-key
    EMBED_MODE=simple
    
    # Server Configuration
    OM_PORT=3000
    OM_API_KEY=openmemory-secret-key  # Optional, for API authentication
    
    # Database
    DB_PATH=./data/openmemory.db
    ```

4.  **Start the server:**
    ```bash
    npm start
    # Server will run on http://localhost:3000
    ```

For more detailed setup instructions, see the [OpenMemory documentation](https://openmemory.cavira.app/).

### Advanced Usage

#### Multi-User Isolation

OpenMemory uses server-side filtering by `user_id` for efficient multi-tenant isolation. The `user_id` is passed as a top-level parameter to leverage OpenMemory's indexed database column, ensuring fast queries and proper tenant isolation in production deployments.

#### App-Level Filtering

When `enable_metadata_tags=True` (default), OpenMemory automatically tags memories with session and app information. This allows you to filter memories by application context, enabling different memory spaces for different applications.

#### Enriched Content Format

OpenMemory uses an enriched content format where author and timestamp metadata are embedded directly in the content string during storage:

```
[Author: user, Time: 2025-11-04T12:34:56] What is the weather today?
```

On retrieval, the service automatically parses this metadata and returns clean content to users. This design avoids N+1 API calls for metadata while preserving context information efficiently.

### Sample Agent

See the [OpenMemory sample agent](https://github.com/google/adk-python/tree/main/contributing/samples/open_memory) in the ADK Python repository for a complete example that demonstrates:

*   Setting up OpenMemoryService with custom configuration
*   Storing session events to memory
*   Retrieving memories across different sessions
*   Using memory in agent conversations

The sample includes setup instructions and shows how to run a complete memory-enabled agent workflow.

## Using Memory in Your Agent

When a memory service is configured, your agent can use a tool or callback to retrieve memories. ADK includes two pre-built tools for retrieving memories:

* `PreloadMemory`: Always retrieve memory at the beginning of each turn (similar to a callback).
* `LoadMemory`: Retrieve memory when your agent decides it would be helpful.

**Example:**

=== "Python"
```python
from google.adk.agents import Agent
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

agent = Agent(
    model=MODEL_ID,
    name='weather_sentiment_agent',
    instruction="...",
    tools=[PreloadMemoryTool()]
)
```

To extract memories from your session, you need to call `add_session_to_memory`. For example, you can automate this via a callback:

=== "Python"
```python
from google import adk

async def auto_save_session_to_memory_callback(callback_context):
    await callback_context._invocation_context.memory_service.add_session_to_memory(
        callback_context._invocation_context.session)

agent = Agent(
    model=MODEL,
    name="Generic_QA_Agent",
    instruction="Answer the user's questions",
    tools=[adk.tools.preload_memory_tool.PreloadMemoryTool()],
    after_agent_callback=auto_save_session_to_memory_callback,
)
```

## Advanced Concepts

### How Memory Works in Practice

The memory workflow internally involves these steps:

1. **Session Interaction:** A user interacts with an agent via a `Session`, managed by a `SessionService`. Events are added, and state might be updated.
2. **Ingestion into Memory:** At some point (often when a session is considered complete or has yielded significant information), your application calls `memory_service.add_session_to_memory(session)`. This extracts relevant information from the session's events and adds it to the long-term knowledge store (in-memory dictionary or Agent Engine Memory Bank).
3. **Later Query:** In a *different* (or the same) session, the user might ask a question requiring past context (e.g., "What did we discuss about project X last week?").
4. **Agent Uses Memory Tool:** An agent equipped with a memory-retrieval tool (like the built-in `load_memory` tool) recognizes the need for past context. It calls the tool, providing a search query (e.g., "discussion project X last week").
5. **Search Execution:** The tool internally calls `memory_service.search_memory(app_name, user_id, query)`.
6. **Results Returned:** The `MemoryService` searches its store (using keyword matching or semantic search) and returns relevant snippets as a `SearchMemoryResponse` containing a list of `MemoryResult` objects (each potentially holding events from a relevant past session).
7. **Agent Uses Results:** The tool returns these results to the agent, usually as part of the context or function response. The agent can then use this retrieved information to formulate its final answer to the user.

### Can an agent have access to more than one memory service?

*   **Through Standard Configuration: No.** The framework (`adk web`, `adk api_server`) is designed to be configured with one single memory service at a time via the `--memory_service_uri` flag. This single service is then provided to the agent and accessed through the built-in `self.search_memory()` method. From a configuration standpoint, you can only choose one backend (`InMemory`, `VertexAiMemoryBankService`, `OpenMemoryService`) for all agents served by that process.

*   **Within Your Agent's Code: Yes, absolutely.** There is nothing preventing you from manually importing and instantiating another memory service directly inside your agent's code. This allows you to access multiple memory sources within a single agent turn.

For example, your agent could use the framework-configured `VertexAiMemoryBankService` to recall conversational history, and also manually instantiate a `OpenMemoryService` to look up information in a self-hosted memory store.

#### Example: Using Two Memory Services

Here’s how you could implement that in your agent's code:

=== "Python"
```python
from google.adk.agents import Agent
from google.adk.memory import InMemoryMemoryService, VertexAiMemoryBankService, OpenMemoryService
from google.genai import types

class MultiMemoryAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.memory_service = InMemoryMemoryService()
        # Manually instantiate a second memory service for document lookups
        self.vertexai_memorybank_service = VertexAiMemoryBankService(
            project="PROJECT_ID",
            location="LOCATION",
            agent_engine_id="AGENT_ENGINE_ID"
        )
        # Or use OpenMemoryService for self-hosted memory
        self.openmemory_service = OpenMemoryService(
            base_url="http://localhost:3000"
        )

    async def run(self, request: types.Content, **kwargs) -> types.Content:
        user_query = request.parts[0].text

        # 1. Search conversational history using the framework-provided memory
        #    (This would be InMemoryMemoryService if configured)
        conversation_context = await self.memory_service.search_memory(query=user_query)

        # 2. Search the document knowledge base using the manually created service
        document_context = await self.vertexai_memorybank_service.search_memory(query=user_query)

        # 3. Search self-hosted memory using OpenMemory
        openmemory_context = await self.openmemory_service.search_memory(query=user_query)

        # Combine the context from all sources to generate a better response
        prompt = "From our past conversations, I remember:\n"
        prompt += f"{conversation_context.memories}\n\n"
        prompt += "From the technical manuals, I found:\n"
        prompt += f"{document_context.memories}\n\n"
        prompt += "From the self-hosted memory, I found:\n"
        prompt += f"{openmemory_context.memories}\n\n"
        prompt += f"Based on all this, here is my answer to '{user_query}':"

        return await self.llm.generate_content_async(prompt)
```
