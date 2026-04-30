# Memory: Long-Term Knowledge with `MemoryService`

Supported in ADKPython v0.1.0Typescript v0.2.0Go v0.1.0Java v0.1.0

We've seen how `Session` tracks the history (`events`) and temporary data (`state`) for a *single, ongoing conversation*. But what if an agent needs to recall information from *past* conversations? This is where the concept of **Long-Term Knowledge** and the **`MemoryService`** come into play.

Think of it this way:

- **`Session` / `State`:** Like your short-term memory during one specific chat.
- **Long-Term Knowledge (`MemoryService`)**: Like a searchable archive or knowledge library the agent can consult, potentially containing information from many past chats or other sources.

## The `MemoryService` Role

The `BaseMemoryService` (or `Service` in Go) defines the interface for managing this searchable, long-term knowledge store. It supports four operations:

1. **Ingesting a session (`add_session_to_memory`):** Take the contents of a (usually completed) `Session` and add relevant information to the long-term knowledge store.
1. **Ingesting events incrementally (`add_events_to_memory`):** Append a delta of events (e.g., the latest turn) without re-ingesting the full session. Useful when you want to write to memory partway through a long-running session.
1. **Writing memory items directly (`add_memory`):** Insert pre-built `MemoryEntry` items, for services that support direct writes alongside event-based extraction.
1. **Searching (`search_memory`):** Allow an agent (typically via a `Tool`) to query the knowledge store and retrieve relevant snippets based on a search query.

Operations 2 and 3 are optional — the base class implementations of `add_events_to_memory` and `add_memory` raise `NotImplementedError`, so check your concrete service before relying on them.

## Choosing the Right Memory Service

The Python ADK ships three `MemoryService` implementations. Use the table below to decide which is the best fit for your agent.

| **Feature**           | **InMemoryMemoryService**                                                         | **VertexAiMemoryBankService**                                                                                                                                                                                      | **VertexAiRagMemoryService**                                                                                                            |
| --------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| **Persistence**       | None (data is lost on restart)                                                    | Yes (Managed by Agent Platform)                                                                                                                                                                                    | Yes (stored in Knowledge Engine)                                                                                                        |
| **Primary Use Case**  | Prototyping, local development, and simple testing.                               | Building meaningful, evolving memories from user conversations.                                                                                                                                                    | Vector-search retrieval over the full conversation corpus, or alongside other RAG-indexed content.                                      |
| **Memory Extraction** | Stores full conversation                                                          | Extracts [meaningful information](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/generate-memories) from conversations and consolidates it with existing memories (powered by LLM) | Stores full conversation, indexed by [Knowledge Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-overview). |
| **Search Capability** | Basic keyword matching.                                                           | Advanced semantic search.                                                                                                                                                                                          | Vector similarity search over Knowledge Engine.                                                                                         |
| **Setup Complexity**  | None. It's the default.                                                           | Low. Requires an [Agent Runtime](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview) instance on Agent Platform.                                                              | Medium. Requires [Knowledge Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/manage-your-rag-corpus).           |
| **Dependencies**      | None.                                                                             | Google Cloud Project, Agent Platform API                                                                                                                                                                           | Google Cloud Project, Knowledge Engine, the Agent Platform SDK (optional install).                                                      |
| **When to use it**    | When you want to search across multiple sessions’ chat histories for prototyping. | When you want your agent to remember and learn from past interactions.                                                                                                                                             | When you already have RAG infrastructure or want to retrieve over raw conversation transcripts.                                         |

`VertexAiRagMemoryService` is only exported from `google.adk.memory` when the Agent Platform SDK is installed. Memory Bank and RAG-backed memory are documented in [Memory Bank](#memory-bank) and [RAG Memory](#rag-memory) below.

## In-Memory Memory

The `InMemoryMemoryService` stores session information in the application's memory and performs basic keyword matching for searches. It requires no setup and is best for prototyping and simple testing scenarios where persistence isn't required.

```py
from google.adk.memory import InMemoryMemoryService
memory_service = InMemoryMemoryService()
```

```typescript
import { InMemoryMemoryService } from '@google/adk';
const memoryService = new InMemoryMemoryService();
```

```go
import (
  "google.golang.org/adk/memory"
  "google.golang.org/adk/session"
)

// Services must be shared across runners to share state and memory.
sessionService := session.InMemoryService()
memoryService := memory.InMemoryService()
```

```java
import com.google.adk.memory.InMemoryMemoryService;

InMemoryMemoryService memoryService = new InMemoryMemoryService();
```

**Example: Adding and Searching Memory**

This example demonstrates the basic flow using the `InMemoryMemoryService` for simplicity.

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

```typescript
import {
    InMemoryMemoryService,
    InMemorySessionService,
    LOAD_MEMORY,
    LlmAgent,
    Runner
} from '@google/adk';
import { createUserContent } from '@google/genai';

// --- Constants ---
const APP_NAME = "memory_example_app";
const USER_ID = "mem_user";
const MODEL = "gemini-2.5-flash";

// --- Agent Definitions ---

// Agent 1: Simple agent to capture information
const infoCaptureAgent = new LlmAgent({
    model: MODEL,
    name: "InfoCaptureAgent",
    instruction: "Acknowledge the user's statement concisely.",
});

// Agent 2: Agent that can use memory
const memoryRecallAgent = new LlmAgent({
    model: MODEL,
    name: "MemoryRecallAgent",
    instruction: "Answer the user's question. Use the 'load_memory' tool if the answer might be in past conversations.",
    tools: [LOAD_MEMORY]
});

// Export for 'adk run' compatibility (to avoid 'No BaseAgent found' error)
export const root_agent = memoryRecallAgent;

// --- Services ---
const sessionService = new InMemorySessionService();
const memoryService = new InMemoryMemoryService();

async function runScenario() {
    // --- Turn 1: Capture some information in a session ---
    console.log("--- Turn 1: Capturing Information ---");
    const runner1 = new Runner({
        agent: infoCaptureAgent,
        appName: APP_NAME,
        sessionService,
        memoryService
    });

    const session1Id = "session_info";
    await sessionService.createSession({ appName: APP_NAME, userId: USER_ID, sessionId: session1Id });
    const userInput1 = createUserContent("My favorite project is Project Alpha.");

    let finalResponseText = "(No final response)";
    for await (const event of runner1.runAsync({ userId: USER_ID, sessionId: session1Id, newMessage: userInput1 })) {
        // Capture any text response from the agent
        if (event.author === infoCaptureAgent.name && event.content?.parts) {
            const text = event.content.parts.map(p => p.text || "").join("").trim();
            if (text) finalResponseText = text;
        }
    }
    console.log(`Agent 1 Response: ${finalResponseText}`);

    // Get the completed session and add to Memory
    const completedSession1 = await sessionService.getSession({ appName: APP_NAME, userId: USER_ID, sessionId: session1Id });
    console.log("\n--- Adding Session 1 to Memory ---");
    if (completedSession1) {
        await memoryService.addSessionToMemory(completedSession1);
        console.log("Session added to memory.");
    }

    // --- Turn 2: Recall the information in a new session ---
    console.log("\n--- Turn 2: Recalling Information ---");
    const runner2 = new Runner({
        agent: memoryRecallAgent,
        appName: APP_NAME,
        sessionService,
        memoryService
    });

    const session2Id = "session_recall";
    await sessionService.createSession({ appName: APP_NAME, userId: USER_ID, sessionId: session2Id });
    const userInput2 = createUserContent("What is my favorite project?");

    let finalResponseText2 = "(No final response)";
    for await (const event of runner2.runAsync({ userId: USER_ID, sessionId: session2Id, newMessage: userInput2 })) {
        // Capture any text response from the agent
        if (event.author === memoryRecallAgent.name && event.content?.parts) {
            const text = event.content.parts.map(p => p.text || "").join("").trim();
            if (text) finalResponseText2 = text;
        }
    }
    console.log(`Agent 2 Response: ${finalResponseText2}`);

    // Exit immediately to prevent the ADK CLI from starting an interactive loop
    process.exit(0);
}

// Execute the scenario
runScenario().catch(err => {
    console.error(err);
    process.exit(1);
});
```

```go
import (
    "context"
    "fmt"
    "log"
    "strings"

    "google.golang.org/adk/agent"
    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/memory"
    "google.golang.org/adk/model/gemini"
    "google.golang.org/adk/runner"
    "google.golang.org/adk/session"
    "google.golang.org/adk/tool"
    "google.golang.org/adk/tool/functiontool"
    "google.golang.org/genai"
)

const (
    appName = "go_memory_example_app"
    userID  = "go_mem_user"
    modelID = "gemini-2.5-flash"
)

// Args defines the input structure for the memory search tool.
type Args struct {
    Query string `json:"query" jsonschema:"The query to search for in the memory."`
}

// Result defines the output structure for the memory search tool.
type Result struct {
    Results []string `json:"results"`
}


// memorySearchToolFunc is the implementation of the memory search tool.
// This function demonstrates accessing memory via tool.Context.
func memorySearchToolFunc(tctx tool.Context, args Args) (Result, error) {
    fmt.Printf("Tool: Searching memory for query: '%s'\n", args.Query)
    // The SearchMemory function is available on the context.
    searchResults, err := tctx.SearchMemory(context.Background(), args.Query)
    if err != nil {
        log.Printf("Error searching memory: %v", err)
        return Result{}, fmt.Errorf("failed memory search")
    }

    var results []string
    for _, res := range searchResults.Memories {
        if res.Content != nil {
            results = append(results, textParts(res.Content)...)
        }
    }
    return Result{Results: results}, nil
}

// Define a tool that can search memory.
var memorySearchTool = must(functiontool.New(
    functiontool.Config{
        Name:        "search_past_conversations",
        Description: "Searches past conversations for relevant information.",
    },
    memorySearchToolFunc,
))


// This example demonstrates how to use the MemoryService in the Go ADK.
// It covers two main scenarios:
// 1. Adding a completed session to memory and recalling it in a new session.
// 2. Searching memory from within a custom tool using the tool.Context.
func main() {
    ctx := context.Background()

    // --- Services ---
    // Services must be shared across runners to share state and memory.
    sessionService := session.InMemoryService()
    memoryService := memory.InMemoryService() // Use in-memory for this demo.

    // --- Scenario 1: Capture information in one session ---
    fmt.Println("--- Turn 1: Capturing Information ---")
    infoCaptureAgent := must(llmagent.New(llmagent.Config{
        Name:        "InfoCaptureAgent",
        Model:       must(gemini.NewModel(ctx, modelID, nil)),
        Instruction: "Acknowledge the user's statement.",
    }))

    runner1 := must(runner.New(runner.Config{
        AppName:        appName,
        Agent:          infoCaptureAgent,
        SessionService: sessionService,
        MemoryService:  memoryService, // Provide the memory service to the Runner
    }))

    session1ID := "session_info"
    must(sessionService.Create(ctx, &session.CreateRequest{AppName: appName, UserID: userID, SessionID: session1ID}))

    userInput1 := genai.NewContentFromText("My favorite project is Project Alpha.", "user")
    var finalResponseText string
    for event, err := range runner1.Run(ctx, userID, session1ID, userInput1, agent.RunConfig{}) {
        if err != nil {
            log.Printf("Agent 1 Error: %v", err)
            continue
        }
        if event.LLMResponse.Content != nil && !event.LLMResponse.Partial {
            finalResponseText = strings.Join(textParts(event.LLMResponse.Content), "")
        }
    }
    fmt.Printf("Agent 1 Response: %s\n", finalResponseText)

    // Add the completed session to the Memory Service
    fmt.Println("\n--- Adding Session 1 to Memory ---")
    resp, err := sessionService.Get(ctx, &session.GetRequest{AppName: appName, UserID: userID, SessionID: session1ID})
    if err != nil {
        log.Fatalf("Failed to get completed session: %v", err)
    }
    if err := memoryService.AddSessionToMemory(ctx, resp.Session); err != nil {
        log.Fatalf("Failed to add session to memory: %v", err)
    }
    fmt.Println("Session added to memory.")

    // --- Scenario 2: Recall the information in a new session using a tool ---
    fmt.Println("\n--- Turn 2: Recalling Information ---")

    memoryRecallAgent := must(llmagent.New(llmagent.Config{
        Name:        "MemoryRecallAgent",
        Model:       must(gemini.NewModel(ctx, modelID, nil)),
        Instruction: "Answer the user's question. Use the 'search_past_conversations' tool if the answer might be in past conversations.",
        Tools:       []tool.Tool{memorySearchTool}, // Give the agent the tool
    }))

    runner2 := must(runner.New(runner.Config{
        Agent:          memoryRecallAgent,
        AppName:        appName,
        SessionService: sessionService,
        MemoryService:  memoryService,
    }))

    session2ID := "session_recall"
    must(sessionService.Create(ctx, &session.CreateRequest{AppName: appName, UserID: userID, SessionID: session2ID}))
    userInput2 := genai.NewContentFromText("What is my favorite project?", "user")

    var finalResponseText2 string
    for event, err := range runner2.Run(ctx, userID, session2ID, userInput2, agent.RunConfig{}) {
        if err != nil {
            log.Printf("Agent 2 Error: %v", err)
            continue
        }
        if event.LLMResponse.Content != nil && !event.LLMResponse.Partial {
            finalResponseText2 = strings.Join(textParts(event.LLMResponse.Content), "")
        }
    }
    fmt.Printf("Agent 2 Response: %s\n", finalResponseText2)
}
```

```java
package com.google.adk.examples.sessions;

import com.google.adk.agents.LlmAgent;
import com.google.adk.memory.InMemoryMemoryService;
import com.google.adk.runner.Runner;
import com.google.adk.sessions.InMemorySessionService;
import com.google.adk.sessions.Session;
import com.google.adk.tools.LoadMemoryTool;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import java.util.Optional;

public class MemoryExample {

  private static final String APP_NAME = "memory_example_app";
  private static final String USER_ID = "mem_user";
  private static final String MODEL = "gemini-flash-latest";

  public static void main(String[] args) {
    // Services
    InMemorySessionService sessionService = new InMemorySessionService();
    InMemoryMemoryService memoryService = new InMemoryMemoryService();

    // Agent 1: Capture
    LlmAgent infoCaptureAgent = new LlmAgent.Builder()
        .model(MODEL)
        .name("InfoCaptureAgent")
        .instruction("Acknowledge the user's statement.")
        .build();

    // Agent 2: Recall
    LlmAgent memoryRecallAgent = new LlmAgent.Builder()
        .model(MODEL)
        .name("MemoryRecallAgent")
        .instruction("Answer the user's question. Use the 'load_memory' tool if the answer might be in past conversations.")
        .tools(new LoadMemoryTool())
        .build();

    // Turn 1
    System.out.println("--- Turn 1: Capturing Information ---");
    Runner runner1 = new Runner.Builder()
        .agent(infoCaptureAgent)
        .appName(APP_NAME)
        .sessionService(sessionService)
        .memoryService(memoryService)
        .build();

    String session1Id = "session_info";
    // Create session
    sessionService.createSession(APP_NAME, USER_ID, null, session1Id).blockingGet();

    Content userInput1 = Content.fromParts(Part.fromText("My favorite project is Project Alpha."));

    runner1.runAsync(USER_ID, session1Id, userInput1)
        .blockingForEach(event -> {
           if (event.finalResponse() && event.content().isPresent()) {
             System.out.println("Agent 1 Response: " + event.content().get().parts().get(0).text().get());
           }
        });

    // Add to memory
    System.out.println("\n--- Adding Session 1 to Memory ---");
    Session completedSession1 = sessionService.getSession(APP_NAME, USER_ID, session1Id, Optional.empty()).blockingGet();
    memoryService.addSessionToMemory(completedSession1).blockingAwait();
    System.out.println("Session added to memory.");

    // Turn 2
    System.out.println("\n--- Turn 2: Recalling Information ---");
    Runner runner2 = new Runner.Builder()
        .agent(memoryRecallAgent)
        .appName(APP_NAME)
        .sessionService(sessionService)
        .memoryService(memoryService)
        .build();

    String session2Id = "session_recall";
    sessionService.createSession(APP_NAME, USER_ID, null, session2Id).blockingGet();

    Content userInput2 = Content.fromParts(Part.fromText("What is my favorite project?"));

    runner2.runAsync(USER_ID, session2Id, userInput2)
        .blockingForEach(event -> {
           if (event.finalResponse() && event.content().isPresent()) {
             System.out.println("Agent 2 Response: " + event.content().get().parts().get(0).text().get());
           }
        });
  }
}
```

### Searching Memory Within a Tool

You can also search memory from within a custom tool by using the tool context.

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

```go
// memorySearchToolFunc is the implementation of the memory search tool.
// This function demonstrates accessing memory via tool.Context.
func memorySearchToolFunc(tctx tool.Context, args Args) (Result, error) {
    fmt.Printf("Tool: Searching memory for query: '%s'\n", args.Query)
    // The SearchMemory function is available on the context.
    searchResults, err := tctx.SearchMemory(context.Background(), args.Query)
    if err != nil {
        log.Printf("Error searching memory: %v", err)
        return Result{}, fmt.Errorf("failed memory search")
    }

    var results []string
    for _, res := range searchResults.Memories {
        if res.Content != nil {
            results = append(results, textParts(res.Content)...)
        }
    }
    return Result{Results: results}, nil
}

// Define a tool that can search memory.
var memorySearchTool = must(functiontool.New(
    functiontool.Config{
        Name:        "search_past_conversations",
        Description: "Searches past conversations for relevant information.",
    },
    memorySearchToolFunc,
))
```

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

## Memory Bank

The `VertexAiMemoryBankService` connects your agent to [Memory Bank](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview), a fully managed Google Cloud service that provides sophisticated, persistent memory capabilities for conversational agents.

### How It Works

The service handles two key operations:

- **Generating Memories:** At the end of a conversation, you can send the session's events to the Memory Bank, which intelligently processes and stores the information as "memories."
- **Retrieving Memories:** Your agent code can issue a search query against the Memory Bank to retrieve relevant memories from past conversations.

### Prerequisites

Before you can use this feature, you must have:

1. **A Google Cloud Project:** With the Agent Platform API enabled.

1. **An Agent Runtime:** You need to create an Agent Runtime on Agent Platform. You do not need to deploy your agent to Agent Runtime to use Memory Bank. This will provide you with the **Agent Runtime ID** required for configuration.

1. **Authentication:** Ensure your local environment is authenticated to access Google Cloud services. The simplest way is to run:

   ```bash
   gcloud auth application-default login
   ```

1. **Environment Variables:** The service requires your Google Cloud Project ID and Location. Set them as environment variables:

   ```bash
   export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
   export GOOGLE_CLOUD_LOCATION="your-gcp-location"
   ```

### Configuration

To connect your agent to the Memory Bank, you use the `--memory_service_uri` flag when starting the ADK server (`adk web` or `adk api_server`). The URI must be in the format `agentengine://<agent_engine_id>`.

bash

```bash
adk web path/to/your/agents_dir --memory_service_uri="agentengine://1234567890"
```

Or, you can configure your agent to use the Memory Bank by manually instantiating the `VertexAiMemoryBankService` and passing it to the `Runner`.

```py
from google import adk
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

## RAG Memory

The `VertexAiRagMemoryService` stores conversations in [Knowledge Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-overview) and retrieves them by vector similarity. Use it when you already have RAG infrastructure or want raw transcript retrieval rather than the LLM-extracted memories produced by Memory Bank. Requires the Agent Platform SDK.

```py
from google.adk.memory import VertexAiRagMemoryService

memory_service = VertexAiRagMemoryService(
    rag_corpus="projects/PROJECT_ID/locations/LOCATION/ragCorpora/CORPUS_ID",
    similarity_top_k=5,
    vector_distance_threshold=0.6,
)
```

## Using Memory in Your Agent

When a memory service is configured, your agent can use a tool or callback to retrieve memories. ADK includes two pre-built tools for retrieving memories:

- `PreloadMemory`: Always retrieve memory at the beginning of each turn (similar to a callback).
- `LoadMemory`: Retrieve memory when your agent decides it would be helpful.

**Example:**

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

```typescript
import { LlmAgent, PRELOAD_MEMORY } from '@google/adk';

const agent = new LlmAgent({
    model: MODEL_ID,
    name: 'weather_sentiment_agent',
    instruction: "...",
    tools: [PRELOAD_MEMORY]
});
```

```go
import (
    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/tool"
    "google.golang.org/adk/tool/preloadmemorytool"
)

agent, _ := llmagent.New(llmagent.Config{
    Model:       model,
    Name:        "weather_sentiment_agent",
    Instruction: "...",
    Tools:       []tool.Tool{preloadmemorytool.New()},
})
```

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

To extract memories from your session, you need to call `add_session_to_memory`. For example, you can automate this via a callback:

```python
from google.adk.agents import Agent
from google import adk

async def auto_save_session_to_memory_callback(callback_context):
    await callback_context.add_session_to_memory()

agent = Agent(
    model=MODEL,
    name="Generic_QA_Agent",
    instruction="Answer the user's questions",
    tools=[adk.tools.preload_memory_tool.PreloadMemoryTool()],
    after_agent_callback=auto_save_session_to_memory_callback,
)
```

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

```go
import (
    "context"
    "google.golang.org/adk/agent"
    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/session"
    "google.golang.org/adk/tool"
    "google.golang.org/adk/tool/loadmemorytool"
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

## Advanced Concepts

### How Memory Works in Practice

The memory workflow internally involves these steps:

1. **Session Interaction:** A user interacts with an agent via a `Session`, managed by a `SessionService`. Events are added, and state might be updated.
1. **Ingestion into Memory:** At some point (often when a session is considered complete or has yielded significant information), your application calls `memory_service.add_session_to_memory(session)`. This extracts relevant information from the session's events and adds it to the long-term knowledge store (in-memory dictionary or Agent Runtime Memory Bank).
1. **Later Query:** In a *different* (or the same) session, the user might ask a question requiring past context (e.g., "What did we discuss about project X last week?").
1. **Agent Uses Memory Tool:** An agent equipped with a memory-retrieval tool (like the built-in `load_memory` tool) recognizes the need for past context. It calls the tool, providing a search query (e.g., "discussion project X last week").
1. **Search Execution:** The tool internally calls `memory_service.search_memory(app_name=..., user_id=..., query=...)`.
1. **Results Returned:** The `MemoryService` searches its store (using keyword matching or semantic search) and returns matching snippets as a `SearchMemoryResponse` containing a list of `MemoryEntry` objects (each holding `content`, optional `author`, optional `timestamp`, and optional `custom_metadata`).
1. **Agent Uses Results:** The tool returns these results to the agent, usually as part of the context or function response. The agent can then use this retrieved information to formulate its final answer to the user.

### Can an agent have access to more than one memory service?

- **Through Standard Configuration: No.** The framework (`adk web`, `adk api_server`) is designed to be configured with one memory service at a time via the `--memory_service_uri` flag. That single service is wired into the runner and exposed through `tool_context.search_memory()` and `callback_context.search_memory()`.
- **Within Your Agent's Code: Yes.** Nothing stops you from importing and instantiating a second `BaseMemoryService` directly. The cleanest place to consult it is from a custom tool, which already has a `ToolContext` for the framework-configured service.

For example, your agent can use the framework-configured `InMemoryMemoryService` for conversation history and manually instantiate a second service (a `VertexAiMemoryBankService`, a `VertexAiRagMemoryService` over a docs corpus, or any other `BaseMemoryService` implementation) for a separate knowledge base.

#### Example: Using Two Memory Services

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
