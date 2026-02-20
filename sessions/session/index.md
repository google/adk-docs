# Session: Tracking Individual Conversations

Supported in ADKPython v0.1.0Typescript v0.2.0Go v0.1.0Java v0.1.0

Following our Introduction, let's dive into the `Session`. Think back to the idea of a "conversation thread." Just like you wouldn't start every text message from scratch, agents need context regarding the ongoing interaction. **`Session`** is the ADK object designed specifically to track and manage these individual conversation threads.

## The `Session` Object

When a user starts interacting with your agent, the `SessionService` creates a `Session` object (`google.adk.sessions.Session`). This object acts as the container holding everything related to that *one specific chat thread*. Here are its key properties:

- **Identification (`id`, `appName`, `userId`):** Unique labels for the conversation.
  - `id`: A unique identifier for *this specific* conversation thread, essential for retrieving it later. A SessionService object can handle multiple `Session`(s). This field identifies which particular session object are we referring to. For example, "test_id_modification".
  - `app_name`: Identifies which agent application this conversation belongs to. For example, "id_modifier_workflow".
  - `userId`: Links the conversation to a particular user.
- **History (`events`):** A chronological sequence of all interactions (`Event` objects – user messages, agent responses, tool actions) that have occurred within this specific thread.
- **Session State (`state`):** A place to store temporary data relevant *only* to this specific, ongoing conversation. This acts as a scratchpad for the agent during the interaction. We will cover how to use and manage `state` in detail in the next section.
- **Activity Tracking (`lastUpdateTime`):** A timestamp indicating the last time an event occurred in this conversation thread.

### Example: Examining Session Properties

```py
 from google.adk.sessions import InMemorySessionService, Session

 # Create a simple session to examine its properties
 temp_service = InMemorySessionService()
 example_session = await temp_service.create_session(
     app_name="my_app",
     user_id="example_user",
     state={"initial_key": "initial_value"} # State can be initialized
 )

 print(f"--- Examining Session Properties ---")
 print(f"ID (`id`):                {example_session.id}")
 print(f"Application Name (`app_name`): {example_session.app_name}")
 print(f"User ID (`user_id`):         {example_session.user_id}")
 print(f"State (`state`):           {example_session.state}") # Note: Only shows initial state here
 print(f"Events (`events`):         {example_session.events}") # Initially empty
 print(f"Last Update (`last_update_time`): {example_session.last_update_time:.2f}")
 print(f"---------------------------------")

 # Clean up (optional for this example)
 temp_service = await temp_service.delete_session(app_name=example_session.app_name,
                             user_id=example_session.user_id, session_id=example_session.id)
 print("The final status of temp_service - ", temp_service)
```

```typescript
 import { InMemorySessionService } from "@google/adk";

 // Create a simple session to examine its properties
 const tempService = new InMemorySessionService();
 const exampleSession = await tempService.createSession({
     appName: "my_app",
     userId: "example_user",
     state: {"initial_key": "initial_value"} // State can be initialized
 });

 console.log("--- Examining Session Properties ---");
 console.log(`ID ('id'):                ${exampleSession.id}`);
 console.log(`Application Name ('appName'): ${exampleSession.appName}`);
 console.log(`User ID ('userId'):         ${exampleSession.userId}`);
 console.log(`State ('state'):           ${JSON.stringify(exampleSession.state)}`); // Note: Only shows initial state here
 console.log(`Events ('events'):         ${JSON.stringify(exampleSession.events)}`); // Initially empty
 console.log(`Last Update ('lastUpdateTime'): ${exampleSession.lastUpdateTime}`);
 console.log("---------------------------------");

 // Clean up (optional for this example)
 const finalStatus = await tempService.deleteSession({
     appName: exampleSession.appName,
     userId: exampleSession.userId,
     sessionId: exampleSession.id
 });
 console.log("The final status of temp_service - ", finalStatus);
```

```go
appName := "my_go_app"
userID := "example_go_user"
initialState := map[string]any{"initial_key": "initial_value"}

// Create a session to examine its properties.
createResp, err := inMemoryService.Create(ctx, &session.CreateRequest{
 AppName: appName,
 UserID:  userID,
 State:   initialState,
})
if err != nil {
 log.Fatalf("Failed to create session: %v", err)
}
exampleSession := createResp.Session

fmt.Println("\n--- Examining Session Properties ---")
fmt.Printf("ID (`ID()`): %s\n", exampleSession.ID())
fmt.Printf("Application Name (`AppName()`): %s\n", exampleSession.AppName())
// To access state, you call Get().
val, _ := exampleSession.State().Get("initial_key")
fmt.Printf("State (`State().Get()`):    initial_key = %v\n", val)

// Events are initially empty.
fmt.Printf("Events (`Events().Len()`):  %d\n", exampleSession.Events().Len())
fmt.Printf("Last Update (`LastUpdateTime()`): %s\n", exampleSession.LastUpdateTime().Format("2006-01-02 15:04:05"))
fmt.Println("---------------------------------")

// Clean up the session.
err = inMemoryService.Delete(ctx, &session.DeleteRequest{
 AppName:   exampleSession.AppName(),
 UserID:    exampleSession.UserID(),
 SessionID: exampleSession.ID(),
})
if err != nil {
 log.Fatalf("Failed to delete session: %v", err)
}
fmt.Println("Session deleted successfully.")
```

```java
 import com.google.adk.sessions.InMemorySessionService;
 import com.google.adk.sessions.Session;
 import java.util.concurrent.ConcurrentMap;
 import java.util.concurrent.ConcurrentHashMap;

 String sessionId = "123";
 String appName = "example-app"; // Example app name
 String userId = "example-user"; // Example user id
 ConcurrentMap<String, Object> initialState = new ConcurrentHashMap<>(Map.of("newKey", "newValue"));
 InMemorySessionService exampleSessionService = new InMemorySessionService();

 // Create Session
 Session exampleSession = exampleSessionService.createSession(
     appName, userId, initialState, Optional.of(sessionId)).blockingGet();
 System.out.println("Session created successfully.");

 System.out.println("--- Examining Session Properties ---");
 System.out.printf("ID (`id`): %s%n", exampleSession.id());
 System.out.printf("Application Name (`appName`): %s%n", exampleSession.appName());
 System.out.printf("User ID (`userId`): %s%n", exampleSession.userId());
 System.out.printf("State (`state`): %s%n", exampleSession.state());
 System.out.println("------------------------------------");


 // Clean up (optional for this example)
 var unused = exampleSessionService.deleteSession(appName, userId, sessionId);
```

\*(\**Note:* *The state shown above is only the initial state. State updates happen via events, as discussed in the State section.)*

## Managing Sessions with a `SessionService`

As seen above, you don't typically create or manage `Session` objects directly. Instead, you use a **`SessionService`**. This service acts as the central manager responsible for the entire lifecycle of your conversation sessions.

Its core responsibilities include:

- **Starting New Conversations:** Creating fresh `Session` objects when a user begins an interaction.
- **Resuming Existing Conversations:** Retrieving a specific `Session` (using its ID) so the agent can continue where it left off.
- **Saving Progress:** Appending new interactions (`Event` objects) to a session's history. This is also the mechanism through which session `state` gets updated (more in the `State` section).
- **Listing Conversations:** Finding the active session threads for a particular user and application.
- **Cleaning Up:** Deleting `Session` objects and their associated data when conversations are finished or no longer needed.

## `SessionService` implementations

ADK provides different `SessionService` implementations, allowing you to choose the storage backend that best suits your needs:

### `InMemorySessionService`

- **How it works:** Stores all session data directly in the application's memory.
- **Persistence:** None. **All conversation data is lost if the application restarts.**
- **Requires:** Nothing extra.
- **Best for:** Quick development, local testing, examples, and scenarios where long-term persistence isn't required.

```py
  from google.adk.sessions import InMemorySessionService
  session_service = InMemorySessionService()
```

```typescript
  import { InMemorySessionService } from "@google/adk";
  const sessionService = new InMemorySessionService();
```

```go
  import "google.golang.org/adk/session"
  inMemoryService := session.InMemoryService()
```

```java
  import com.google.adk.sessions.InMemorySessionService;
  InMemorySessionService exampleSessionService = new InMemorySessionService();
```

### `VertexAiSessionService`

Supported in ADKPython v0.1.0Go v0.1.0Java v0.1.0

- **How it works:** Uses Google Cloud Vertex AI infrastructure via API calls for session management.
- **Persistence:** Yes. Data is managed reliably and scalably via [Vertex AI Agent Engine](https://google.github.io/adk-docs/deploy/agent-engine/).
- **Requires:**
  - A Google Cloud project (`pip install vertexai`)
  - A Google Cloud storage bucket that can be configured by this [step](https://cloud.google.com/vertex-ai/docs/pipelines/configure-project#storage).
  - A Reasoning Engine resource name/ID that can setup following this [tutorial](https://google.github.io/adk-docs/deploy/agent-engine/).
  - If you do not have a Google Cloud project and you want to try the VertexAiSessionService, see [Vertex AI Express Mode](/adk-docs/tools/google-cloud/express-mode/).
- **Best for:** Scalable production applications deployed on Google Cloud, especially when integrating with other Vertex AI features.

```py
# Requires: pip install google-adk[vertexai]
# Plus GCP setup and authentication
from google.adk.sessions import VertexAiSessionService

PROJECT_ID = "your-gcp-project-id"
LOCATION = "us-central1"
# The app_name used with this service should be the Reasoning Engine ID or name
REASONING_ENGINE_APP_NAME = "projects/your-gcp-project-id/locations/us-central1/reasoningEngines/your-engine-id"

session_service = VertexAiSessionService(project=PROJECT_ID, location=LOCATION)
# Use REASONING_ENGINE_APP_NAME when calling service methods, e.g.:
# session_service = await session_service.create_session(app_name=REASONING_ENGINE_APP_NAME, ...)
```

```go
import "google.golang.org/adk/session"

// 2. VertexAIService
// Before running, ensure your environment is authenticated:
// gcloud auth application-default login
// export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
// export GOOGLE_CLOUD_LOCATION="your-gcp-location"

modelName := "gemini-flash-latest" // Replace with your desired model
vertexService, err := session.VertexAIService(ctx, modelName)
if err != nil {
  log.Printf("Could not initialize VertexAIService (this is expected if the gcloud project is not set): %v", err)
} else {
  fmt.Println("Successfully initialized VertexAIService.")
}
```

```java
// Please look at the set of requirements above, consequently export the following in your bashrc file:
// export GOOGLE_CLOUD_PROJECT=my_gcp_project
// export GOOGLE_CLOUD_LOCATION=us-central1
// export GOOGLE_API_KEY=my_api_key

import com.google.adk.sessions.VertexAiSessionService;
import java.util.UUID;

String sessionId = UUID.randomUUID().toString();
String reasoningEngineAppName = "123456789";
String userId = "u_123"; // Example user id
ConcurrentMap<String, Object> initialState = new
    ConcurrentHashMap<>(); // No initial state needed for this example

VertexAiSessionService sessionService = new VertexAiSessionService();
Session mySession =
    sessionService
        .createSession(reasoningEngineAppName, userId, initialState, Optional.of(sessionId))
        .blockingGet();
```

### `DatabaseSessionService`

Supported in ADKPython v0.1.0Go v0.1.0

- **How it works:** Connects to a relational database (e.g., PostgreSQL, MySQL, SQLite) to store session data persistently in tables.
- **Persistence:** Yes. Data survives application restarts.
- **Requires:** A configured database.
- **Best for:** Applications needing reliable, persistent storage that you manage yourself.

```py
from google.adk.sessions import DatabaseSessionService
# Example using a local SQLite file:
# Note: The implementation requires an async database driver.
# For SQLite, use 'sqlite+aiosqlite' instead of 'sqlite' to ensure async compatibility.
db_url = "sqlite+aiosqlite:///./my_agent_data.db"
session_service = DatabaseSessionService(db_url=db_url)
```

Async Driver Requirement

`DatabaseSessionService` requires an async database driver. When using SQLite, you must use `sqlite+aiosqlite` instead of `sqlite` in your connection string. For other databases (PostgreSQL, MySQL), ensure you're using an async-compatible driver, such as `asyncpg` for PostgreSQL, `aiomysql` for MySQL.

Session database schema change in ADK Python v1.22.0

The schema for the session database changed in ADK Python v1.22.0, which requires migration of the Session Database. For more information, see [Session database schema migration](/adk-docs/sessions/session/migrate/).

## The Session Lifecycle

Here’s a simplified flow of how `Session` and `SessionService` work together during a conversation turn:

1. **Start or Resume:** Your application needs to use the `SessionService` to either `create_session` (for a new chat) or use an existing session id.
1. **Context Provided:** The `Runner` gets the appropriate `Session` object from the appropriate service method, providing the agent with access to the corresponding Session's `state` and `events`.
1. **Agent Processing:** The user prompts the agent with a query. The agent analyzes the query and potentially the session `state` and `events` history to determine the response.
1. **Response & State Update:** The agent generates a response (and potentially flags data to be updated in the `state`). The `Runner` packages this as an `Event`.
1. **Save Interaction:** The `Runner` calls `sessionService.append_event(session, event)` with the `session` and the new `event` as the arguments. The service adds the `Event` to the history and updates the session's `state` in storage based on information within the event. The session's `last_update_time` also get updated.
1. **Ready for Next:** The agent's response goes to the user. The updated `Session` is now stored by the `SessionService`, ready for the next turn (which restarts the cycle at step 1, usually with the continuation of the conversation in the current session).
1. **End Conversation:** When the conversation is over, your application calls `sessionService.delete_session(...)` to clean up the stored session data if it is no longer required.

This cycle highlights how the `SessionService` ensures conversational continuity by managing the history and state associated with each `Session` object.
