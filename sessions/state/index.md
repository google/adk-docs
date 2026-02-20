# State: The Session's Scratchpad

Supported in ADKPython v0.1.0TypeScript v0.2.0Go v0.1.0Java v0.1.0

Within each `Session` (our conversation thread), the **`state`** attribute acts like the agent's dedicated scratchpad for that specific interaction. While `session.events` holds the full history, `session.state` is where the agent stores and updates dynamic details needed *during* the conversation.

## What is `session.state`?

Conceptually, `session.state` is a collection (dictionary or Map) holding key-value pairs. It's designed for information the agent needs to recall or track to make the current conversation effective:

- **Personalize Interaction:** Remember user preferences mentioned earlier (e.g., `'user_preference_theme': 'dark'`).
- **Track Task Progress:** Keep tabs on steps in a multi-turn process (e.g., `'booking_step': 'confirm_payment'`).
- **Accumulate Information:** Build lists or summaries (e.g., `'shopping_cart_items': ['book', 'pen']`).
- **Make Informed Decisions:** Store flags or values influencing the next response (e.g., `'user_is_authenticated': True`).

### Key Characteristics of `State`

1. **Structure: Serializable Key-Value Pairs**

   - Data is stored as `key: value`.
   - **Keys:** Always strings (`str`). Use clear names (e.g., `'departure_city'`, `'user:language_preference'`).
   - **Values:** Must be **serializable**. This means they can be easily saved and loaded by the `SessionService`. Stick to basic types in the specific languages (Python/Go/Java/TypeScript) like strings, numbers, booleans, and simple lists or dictionaries containing *only* these basic types. (See API documentation for precise details).
   - **⚠️ Avoid Complex Objects:** **Do not store non-serializable objects** (custom class instances, functions, connections, etc.) directly in the state. Store simple identifiers if needed, and retrieve the complex object elsewhere.

1. **Mutability: It Changes**

   - The contents of the `state` are expected to change as the conversation evolves.

1. **Persistence: Depends on `SessionService`**

   - Whether state survives application restarts depends on your chosen service:
   - `InMemorySessionService`: **Not Persistent.** State is lost on restart.
   - `DatabaseSessionService` / `VertexAiSessionService`: **Persistent.** State is saved reliably.

Note

The specific parameters or method names for the primitives may vary slightly by SDK language (e.g., `session.state['current_intent'] = 'book_flight'` in Python,`context.State().Set("current_intent", "book_flight")` in Go, `session.state().put("current_intent", "book_flight)` in Java, or `context.state.set("current_intent", "book_flight")` in TypeScript). Refer to the language-specific API documentation for details.

### Organizing State with Prefixes: Scope Matters

Prefixes on state keys define their scope and persistence behavior, especially with persistent services:

- **No Prefix (Session State):**

  - **Scope:** Specific to the *current* session (`id`).
  - **Persistence:** Only persists if the `SessionService` is persistent (`Database`, `VertexAI`).
  - **Use Cases:** Tracking progress within the current task (e.g., `'current_booking_step'`), temporary flags for this interaction (e.g., `'needs_clarification'`).
  - **Example:** `session.state['current_intent'] = 'book_flight'`

- **`user:` Prefix (User State):**

  - **Scope:** Tied to the `user_id`, shared across *all* sessions for that user (within the same `app_name`).
  - **Persistence:** Persistent with `Database` or `VertexAI`. (Stored by `InMemory` but lost on restart).
  - **Use Cases:** User preferences (e.g., `'user:theme'`), profile details (e.g., `'user:name'`).
  - **Example:** `session.state['user:preferred_language'] = 'fr'`

- **`app:` Prefix (App State):**

  - **Scope:** Tied to the `app_name`, shared across *all* users and sessions for that application.
  - **Persistence:** Persistent with `Database` or `VertexAI`. (Stored by `InMemory` but lost on restart).
  - **Use Cases:** Global settings (e.g., `'app:api_endpoint'`), shared templates.
  - **Example:** `session.state['app:global_discount_code'] = 'SAVE10'`

- **`temp:` Prefix (Temporary Invocation State):**

  - **Scope:** Specific to the current **invocation** (the entire process from an agent receiving user input to generating the final output for that input).
  - **Persistence:** **Not Persistent.** Discarded after the invocation completes and does not carry over to the next one.
  - **Use Cases:** Storing intermediate calculations, flags, or data passed between tool calls within a single invocation.
  - **When Not to Use:** For information that must persist across different invocations, such as user preferences, conversation history summaries, or accumulated data.
  - **Example:** `session.state['temp:raw_api_response'] = {...}`

Sub-Agents and Invocation Context

When a parent agent calls a sub-agent (e.g., using `SequentialAgent` or `ParallelAgent`), it passes its `InvocationContext` to the sub-agent. This means the entire chain of agent calls shares the same invocation ID and, therefore, the same `temp:` state.

**How the Agent Sees It:** Your agent code interacts with the *combined* state through the single `session.state` collection (dict/ Map). The `SessionService` handles fetching/merging state from the correct underlying storage based on prefixes.

### Accessing Session State in Agent Instructions

When working with `LlmAgent` instances, you can directly inject session state values into the agent's instruction string using a simple templating syntax. This allows you to create dynamic and context-aware instructions without relying solely on natural language directives.

#### Using `{key}` Templating

To inject a value from the session state, enclose the key of the desired state variable within curly braces: `{key}`. The framework will automatically replace this placeholder with the corresponding value from `session.state` before passing the instruction to the LLM.

**Example:**

```python
from google.adk.agents import LlmAgent

story_generator = LlmAgent(
    name="StoryGenerator",
    model="gemini-2.0-flash",
    instruction="""Write a short story about a cat, focusing on the theme: {topic}."""
)

# Assuming session.state['topic'] is set to "friendship", the LLM
# will receive the following instruction:
# "Write a short story about a cat, focusing on the theme: friendship."
```

```typescript
import { LlmAgent } from "@google/adk";

const storyGenerator = new LlmAgent({
    name: "StoryGenerator",
    model: "gemini-2.5-flash",
    instruction: "Write a short story about a cat, focusing on the theme: {topic}."
});

// Assuming session.state['topic'] is set to "friendship", the LLM
// will receive the following instruction:
// "Write a short story about a cat, focusing on the theme: friendship."
```

```go
func main() {
    ctx := context.Background()
    sessionService := session.InMemoryService()

    // 1. Initialize a session with a 'topic' in its state.
    _, err := sessionService.Create(ctx, &session.CreateRequest{
        AppName:   appName,
        UserID:    userID,
        SessionID: sessionID,
        State: map[string]any{
            "topic": "friendship",
        },
    })
    if err != nil {
        log.Fatalf("Failed to create session: %v", err)
    }

    // 2. Create an agent with an instruction that uses a {topic} placeholder.
    //    The ADK will automatically inject the value of "topic" from the
    //    session state into the instruction before calling the LLM.
    model, err := gemini.NewModel(ctx, modelID, nil)
    if err != nil {
        log.Fatalf("Failed to create Gemini model: %v", err)
    }
    storyGenerator, err := llmagent.New(llmagent.Config{
        Name:        "StoryGenerator",
        Model:       model,
        Instruction: "Write a short story about a cat, focusing on the theme: {topic}.",
    })
    if err != nil {
        log.Fatalf("Failed to create agent: %v", err)
    }

    r, err := runner.New(runner.Config{
        AppName:        appName,
        Agent:          agent.Agent(storyGenerator),
        SessionService: sessionService,
    })
    if err != nil {
        log.Fatalf("Failed to create runner: %v", err)
    }
```

#### Important Considerations

- Key Existence: Ensure that the key you reference in the instruction string exists in the session.state. If the key is missing, the agent will throw an error. To use a key that may or may not be present, you can include a question mark (?) after the key (e.g. {topic?}).
- Data Types: The value associated with the key should be a string or a type that can be easily converted to a string.
- Escaping: If you need to use literal curly braces in your instruction (e.g., for JSON formatting), you'll need to escape them.

#### Bypassing State Injection with `InstructionProvider`

In some cases, you might want to use `{{` and `}}` literally in your instructions without triggering the state injection mechanism. For example, you might be writing instructions for an agent that helps with a templating language that uses the same syntax.

To achieve this, you can provide a function to the `instruction` parameter instead of a string. This function is called an `InstructionProvider`. When you use an `InstructionProvider`, the ADK will not attempt to inject state, and your instruction string will be passed to the model as-is.

The `InstructionProvider` function receives a `ReadonlyContext` object, which you can use to access session state or other contextual information if you need to build the instruction dynamically.

```python
from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext

# This is an InstructionProvider
def my_instruction_provider(context: ReadonlyContext) -> str:
    # You can optionally use the context to build the instruction
    # For this example, we'll return a static string with literal braces.
    return "This is an instruction with {{literal_braces}} that will not be replaced."

agent = LlmAgent(
    model="gemini-2.0-flash",
    name="template_helper_agent",
    instruction=my_instruction_provider
)
```

```typescript
import { LlmAgent, ReadonlyContext } from "@google/adk";

// This is an InstructionProvider
function myInstructionProvider(context: ReadonlyContext): string {
    // You can optionally use the context to build the instruction
    // For this example, we'll return a static string with literal braces.
    return "This is an instruction with {{literal_braces}} that will not be replaced.";
}

const agent = new LlmAgent({
    model: "gemini-2.5-flash",
    name: "template_helper_agent",
    instruction: myInstructionProvider
});
```

```go
//  1. This InstructionProvider returns a static string.
//     Because it's a provider function, the ADK will not attempt to inject
//     state, and the instruction will be passed to the model as-is,
//     preserving the literal braces.
func staticInstructionProvider(ctx agent.ReadonlyContext) (string, error) {
    return "This is an instruction with {{literal_braces}} that will not be replaced.", nil
}
```

If you want to both use an `InstructionProvider` *and* inject state into your instructions, you can use the `inject_session_state` utility function.

```python
from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.utils import instructions_utils

async def my_dynamic_instruction_provider(context: ReadonlyContext) -> str:
    template = "This is a {adjective} instruction with {{literal_braces}}."
    # This will inject the 'adjective' state variable but leave the literal braces.
    return await instructions_utils.inject_session_state(template, context)

agent = LlmAgent(
    model="gemini-2.0-flash",
    name="dynamic_template_helper_agent",
    instruction=my_dynamic_instruction_provider
)
```

```go
//  2. This InstructionProvider demonstrates how to manually inject state
//     while also preserving literal braces. It uses the instructionutil helper.
func dynamicInstructionProvider(ctx agent.ReadonlyContext) (string, error) {
    template := "This is a {adjective} instruction with {{literal_braces}}."
    // This will inject the 'adjective' state variable but leave the literal braces.
    return instructionutil.InjectSessionState(ctx, template)
}
```

**Benefits of Direct Injection**

- Clarity: Makes it explicit which parts of the instruction are dynamic and based on session state.
- Reliability: Avoids relying on the LLM to correctly interpret natural language instructions to access state.
- Maintainability: Simplifies instruction strings and reduces the risk of errors when updating state variable names.

**Relation to Other State Access Methods**

This direct injection method is specific to LlmAgent instructions. Refer to the following section for more information on other state access methods.

### How State is Updated: Recommended Methods

The Right Way to Modify State

When you need to change the session state, the correct and safest method is to **directly modify the `state` object on the `Context`** provided to your function (e.g., `callback_context.state['my_key'] = 'new_value'`). This is considered "direct state manipulation" in the right way, as the framework automatically tracks these changes.

This is critically different from directly modifying the `state` on a `Session` object you retrieve from the `SessionService` (e.g., `my_session.state['my_key'] = 'new_value'`). **You should avoid this**, as it bypasses the ADK's event tracking and can lead to lost data. The "Warning" section at the end of this page has more details on this important distinction.

State should **always** be updated as part of adding an `Event` to the session history using `session_service.append_event()`. This ensures changes are tracked, persistence works correctly, and updates are thread-safe.

**1. The Easy Way: `output_key` (for Agent Text Responses)**

This is the simplest method for saving an agent's final text response directly into the state. When defining your `LlmAgent`, specify the `output_key`:

```py
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService, Session
from google.adk.runners import Runner
from google.genai.types import Content, Part

# Define agent with output_key
greeting_agent = LlmAgent(
    name="Greeter",
    model="gemini-2.0-flash", # Use a valid model
    instruction="Generate a short, friendly greeting.",
    output_key="last_greeting" # Save response to state['last_greeting']
)

# --- Setup Runner and Session ---
app_name, user_id, session_id = "state_app", "user1", "session1"
session_service = InMemorySessionService()
runner = Runner(
    agent=greeting_agent,
    app_name=app_name,
    session_service=session_service
)
session = await session_service.create_session(app_name=app_name,
                                    user_id=user_id,
                                    session_id=session_id)
print(f"Initial state: {session.state}")

# --- Run the Agent ---
# Runner handles calling append_event, which uses the output_key
# to automatically create the state_delta.
user_message = Content(parts=[Part(text="Hello")])
for event in runner.run(user_id=user_id,
                        session_id=session_id,
                        new_message=user_message):
    if event.is_final_response():
      print(f"Agent responded.") # Response text is also in event.content

# --- Check Updated State ---
updated_session = await session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)
print(f"State after agent run: {updated_session.state}")
# Expected output might include: {'last_greeting': 'Hello there! How can I help you today?'}
```

```typescript
import { LlmAgent, Runner, InMemorySessionService, isFinalResponse } from "@google/adk";
import { Content } from "@google/genai";

// Define agent with outputKey
const greetingAgent = new LlmAgent({
    name: "Greeter",
    model: "gemini-2.5-flash",
    instruction: "Generate a short, friendly greeting.",
    outputKey: "last_greeting" // Save response to state['last_greeting']
});

// --- Setup Runner and Session ---
const appName = "state_app";
const userId = "user1";
const sessionId = "session1";
const sessionService = new InMemorySessionService();
const runner = new Runner({
    agent: greetingAgent,
    appName: appName,
    sessionService: sessionService
});
const session = await sessionService.createSession({
    appName,
    userId,
    sessionId
});
console.log(`Initial state: ${JSON.stringify(session.state)}`);

// --- Run the Agent ---
// Runner handles calling appendEvent, which uses the outputKey
// to automatically create the stateDelta.
const userMessage: Content = { parts: [{ text: "Hello" }] };
for await (const event of runner.runAsync({
    userId,
    sessionId,
    newMessage: userMessage
})) {
    if (isFinalResponse(event)) {
      console.log("Agent responded."); // Response text is also in event.content
    }
}

// --- Check Updated State ---
const updatedSession = await sessionService.getSession({ appName, userId, sessionId });
console.log(`State after agent run: ${JSON.stringify(updatedSession?.state)}`);
// Expected output might include: {"last_greeting":"Hello there! How can I help you today?"}
```

```go
//  1. GreetingAgent demonstrates using `OutputKey` to save an agent's
//     final text response directly into the session state.
func greetingAgentExample(sessionService session.Service) {
    fmt.Println("--- Running GreetingAgent (output_key) Example ---")
    ctx := context.Background()

    modelGreeting, err := gemini.NewModel(ctx, modelID, nil)
    if err != nil {
        log.Fatalf("Failed to create Gemini model for greeting agent: %v", err)
    }
    greetingAgent, err := llmagent.New(llmagent.Config{
        Name:        "Greeter",
        Model:       modelGreeting,
        Instruction: "Generate a short, friendly greeting.",
        OutputKey:   "last_greeting",
    })
    if err != nil {
        log.Fatalf("Failed to create greeting agent: %v", err)
    }

    r, err := runner.New(runner.Config{
        AppName:        appName,
        Agent:          agent.Agent(greetingAgent),
        SessionService: sessionService,
    })
    if err != nil {
        log.Fatalf("Failed to create runner: %v", err)
    }

    // Run the agent
    userMessage := genai.NewContentFromText("Hello", "user")
    for event, err := range r.Run(ctx, userID, sessionID, userMessage, agent.RunConfig{}) {
        if err != nil {
            log.Printf("Agent Error: %v", err)
            continue
        }
        if isFinalResponse(event) {
            if event.LLMResponse.Content != nil {
                fmt.Printf("Agent responded with: %q\n", textParts(event.LLMResponse.Content))
            } else {
                fmt.Println("Agent responded.")
            }
        }
    }

    // Check the updated state
    resp, err := sessionService.Get(ctx, &session.GetRequest{AppName: appName, UserID: userID, SessionID: sessionID})
    if err != nil {
        log.Fatalf("Failed to get session: %v", err)
    }
    lastGreeting, _ := resp.Session.State().Get("last_greeting")
    fmt.Printf("State after agent run: last_greeting = %q\n\n", lastGreeting)
}
```

```java
import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.RunConfig;
import com.google.adk.events.Event;
import com.google.adk.runner.Runner;
import com.google.adk.sessions.InMemorySessionService;
import com.google.adk.sessions.Session;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import java.util.List;
import java.util.Optional;

public class GreetingAgentExample {

  public static void main(String[] args) {
    // Define agent with output_key
    LlmAgent greetingAgent =
        LlmAgent.builder()
            .name("Greeter")
            .model("gemini-2.0-flash")
            .instruction("Generate a short, friendly greeting.")
            .description("Greeting agent")
            .outputKey("last_greeting") // Save response to state['last_greeting']
            .build();

    // --- Setup Runner and Session ---
    String appName = "state_app";
    String userId = "user1";
    String sessionId = "session1";

    InMemorySessionService sessionService = new InMemorySessionService();
    Runner runner = new Runner(greetingAgent, appName, null, sessionService); // artifactService can be null if not used

    Session session =
        sessionService.createSession(appName, userId, null, sessionId).blockingGet();
    System.out.println("Initial state: " + session.state().entrySet());

    // --- Run the Agent ---
    // Runner handles calling appendEvent, which uses the output_key
    // to automatically create the stateDelta.
    Content userMessage = Content.builder().parts(List.of(Part.fromText("Hello"))).build();

    // RunConfig is needed for runner.runAsync in Java
    RunConfig runConfig = RunConfig.builder().build();

    for (Event event : runner.runAsync(userId, sessionId, userMessage, runConfig).blockingIterable()) {
      if (event.finalResponse()) {
        System.out.println("Agent responded."); // Response text is also in event.content
      }
    }

    // --- Check Updated State ---
    Session updatedSession =
        sessionService.getSession(appName, userId, sessionId, Optional.empty()).blockingGet();
    assert updatedSession != null;
    System.out.println("State after agent run: " + updatedSession.state().entrySet());
    // Expected output might include: {'last_greeting': 'Hello there! How can I help you today?'}
  }
}
```

Behind the scenes, the `Runner` uses the `output_key` to create the necessary `EventActions` with a `state_delta` and calls `append_event`.

**2. The Standard Way: `EventActions.state_delta` (for Complex Updates)**

For more complex scenarios (updating multiple keys, non-string values, specific scopes like `user:` or `app:`, or updates not tied directly to the agent's final text), you manually construct the `state_delta` within `EventActions`.

```py
from google.adk.sessions import InMemorySessionService, Session
from google.adk.events import Event, EventActions
from google.genai.types import Part, Content
import time

# --- Setup ---
session_service = InMemorySessionService()
app_name, user_id, session_id = "state_app_manual", "user2", "session2"
session = await session_service.create_session(
    app_name=app_name,
    user_id=user_id,
    session_id=session_id,
    state={"user:login_count": 0, "task_status": "idle"}
)
print(f"Initial state: {session.state}")

# --- Define State Changes ---
current_time = time.time()
state_changes = {
    "task_status": "active",              # Update session state
    "user:login_count": session.state.get("user:login_count", 0) + 1, # Update user state
    "user:last_login_ts": current_time,   # Add user state
    "temp:validation_needed": True        # Add temporary state (will be discarded)
}

# --- Create Event with Actions ---
actions_with_update = EventActions(state_delta=state_changes)
# This event might represent an internal system action, not just an agent response
system_event = Event(
    invocation_id="inv_login_update",
    author="system", # Or 'agent', 'tool' etc.
    actions=actions_with_update,
    timestamp=current_time
    # content might be None or represent the action taken
)

# --- Append the Event (This updates the state) ---
await session_service.append_event(session, system_event)
print("`append_event` called with explicit state delta.")

# --- Check Updated State ---
updated_session = await session_service.get_session(app_name=app_name,
                                            user_id=user_id,
                                            session_id=session_id)
print(f"State after event: {updated_session.state}")
# Expected: {'user:login_count': 1, 'task_status': 'active', 'user:last_login_ts': <timestamp>}
# Note: 'temp:validation_needed' is NOT present.
```

```typescript
import { InMemorySessionService, createEvent, createEventActions } from "@google/adk";

// --- Setup ---
const sessionService = new InMemorySessionService();
const appName = "state_app_manual";
const userId = "user2";
const sessionId = "session2";
const session = await sessionService.createSession({
    appName,
    userId,
    sessionId,
    state: { "user:login_count": 0, "task_status": "idle" }
});
console.log(`Initial state: ${JSON.stringify(session.state)}`);

// --- Define State Changes ---
const currentTime = Date.now();
const stateChanges = {
    "task_status": "active",              // Update session state
    "user:login_count": (session.state["user:login_count"] as number || 0) + 1, // Update user state
    "user:last_login_ts": currentTime,   // Add user state
    "temp:validation_needed": true        // Add temporary state (will be discarded)
};

// --- Create Event with Actions ---
const actionsWithUpdate = createEventActions({
    stateDelta: stateChanges,
});
// This event might represent an internal system action, not just an agent response
const systemEvent = createEvent({
    invocationId: "inv_login_update",
    author: "system", // Or 'agent', 'tool' etc.
    actions: actionsWithUpdate,
    timestamp: currentTime
    // content might be null or represent the action taken
});

// --- Append the Event (This updates the state) ---
await sessionService.appendEvent({ session, event: systemEvent });
console.log("`appendEvent` called with explicit state delta.");

// --- Check Updated State ---
const updatedSession = await sessionService.getSession({
    appName,
    userId,
    sessionId
});
console.log(`State after event: ${JSON.stringify(updatedSession?.state)}`);
// Expected: {"user:login_count":1,"task_status":"active","user:last_login_ts":<timestamp>}
// Note: 'temp:validation_needed' is NOT present.
```

```go
//  2. manualStateUpdateExample demonstrates creating an event with explicit
//     state changes (a "state_delta") to update multiple keys, including
//     those with user- and temp- prefixes.
func manualStateUpdateExample(sessionService session.Service) {
    fmt.Println("--- Running Manual State Update (EventActions) Example ---")
    ctx := context.Background()
    s, err := sessionService.Get(ctx, &session.GetRequest{AppName: appName, UserID: userID, SessionID: sessionID})
    if err != nil {
        log.Fatalf("Failed to get session: %v", err)
    }
    retrievedSession := s.Session

    // Define state changes
    loginCount, _ := retrievedSession.State().Get("user:login_count")
    newLoginCount := 1
    if lc, ok := loginCount.(int); ok {
        newLoginCount = lc + 1
    }

    stateChanges := map[string]any{
        "task_status":            "active",
        "user:login_count":       newLoginCount,
        "user:last_login_ts":     time.Now().Unix(),
        "temp:validation_needed": true,
    }

    // Create an event with the state changes
    systemEvent := session.NewEvent("inv_login_update")
    systemEvent.Author = "system"
    systemEvent.Actions.StateDelta = stateChanges

    // Append the event to update the state
    if err := sessionService.AppendEvent(ctx, retrievedSession, systemEvent); err != nil {
        log.Fatalf("Failed to append event: %v", err)
    }
    fmt.Println("`append_event` called with explicit state delta.")

    // Check the updated state
    updatedResp, err := sessionService.Get(ctx, &session.GetRequest{AppName: appName, UserID: userID, SessionID: sessionID})
    if err != nil {
        log.Fatalf("Failed to get session: %v", err)
    }
    taskStatus, _ := updatedResp.Session.State().Get("task_status")
    loginCount, _ = updatedResp.Session.State().Get("user:login_count")
    lastLogin, _ := updatedResp.Session.State().Get("user:last_login_ts")
    temp, err := updatedResp.Session.State().Get("temp:validation_needed") // This should fail or be nil

    fmt.Printf("State after event: task_status=%q, user:login_count=%v, user:last_login_ts=%v\n", taskStatus, loginCount, lastLogin)
    if err != nil {
        fmt.Printf("As expected, temp state was not persisted: %v\n\n", err)
    } else {
        fmt.Printf("Unexpected temp state value: %v\n\n", temp)
    }
}
```

```java
import com.google.adk.events.Event;
import com.google.adk.events.EventActions;
import com.google.adk.sessions.InMemorySessionService;
import com.google.adk.sessions.Session;
import java.time.Instant;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

public class ManualStateUpdateExample {

  public static void main(String[] args) {
    // --- Setup ---
    InMemorySessionService sessionService = new InMemorySessionService();
    String appName = "state_app_manual";
    String userId = "user2";
    String sessionId = "session2";

    ConcurrentMap<String, Object> initialState = new ConcurrentHashMap<>();
    initialState.put("user:login_count", 0);
    initialState.put("task_status", "idle");

    Session session =
        sessionService.createSession(appName, userId, initialState, sessionId).blockingGet();
    System.out.println("Initial state: " + session.state().entrySet());

    // --- Define State Changes ---
    long currentTimeMillis = Instant.now().toEpochMilli(); // Use milliseconds for Java Event

    ConcurrentMap<String, Object> stateChanges = new ConcurrentHashMap<>();
    stateChanges.put("task_status", "active"); // Update session state

    // Retrieve and increment login_count
    Object loginCountObj = session.state().get("user:login_count");
    int currentLoginCount = 0;
    if (loginCountObj instanceof Number) {
      currentLoginCount = ((Number) loginCountObj).intValue();
    }
    stateChanges.put("user:login_count", currentLoginCount + 1); // Update user state

    stateChanges.put("user:last_login_ts", currentTimeMillis); // Add user state (as long milliseconds)
    stateChanges.put("temp:validation_needed", true); // Add temporary state

    // --- Create Event with Actions ---
    EventActions actionsWithUpdate = EventActions.builder().stateDelta(stateChanges).build();

    // This event might represent an internal system action, not just an agent response
    Event systemEvent =
        Event.builder()
            .invocationId("inv_login_update")
            .author("system") // Or 'agent', 'tool' etc.
            .actions(actionsWithUpdate)
            .timestamp(currentTimeMillis)
            // content might be None or represent the action taken
            .build();

    // --- Append the Event (This updates the state) ---
    sessionService.appendEvent(session, systemEvent).blockingGet();
    System.out.println("`appendEvent` called with explicit state delta.");

    // --- Check Updated State ---
    Session updatedSession =
        sessionService.getSession(appName, userId, sessionId, Optional.empty()).blockingGet();
    assert updatedSession != null;
    System.out.println("State after event: " + updatedSession.state().entrySet());
    // Expected: {'user:login_count': 1, 'task_status': 'active', 'user:last_login_ts': <timestamp_millis>}
    // Note: 'temp:validation_needed' is NOT present because InMemorySessionService's appendEvent
    // applies delta to its internal user/app state maps IF keys have prefixes,
    // and to the session's own state map (which is then merged on getSession).
  }
}
```

**3. Via `CallbackContext` or `ToolContext` (Recommended for Callbacks and Tools)**

Modifying state within agent callbacks (e.g., `on_before_agent_call`, `on_after_agent_call`) or tool functions is best done using the `state` attribute of the `CallbackContext` or `ToolContext` provided to your function.

- `callback_context.state['my_key'] = my_value`
- `tool_context.state['my_key'] = my_value`

These context objects are specifically designed to manage state changes within their respective execution scopes. When you modify `context.state`, the ADK framework ensures that these changes are automatically captured and correctly routed into the `EventActions.state_delta` for the event being generated by the callback or tool. This delta is then processed by the `SessionService` when the event is appended, ensuring proper persistence and tracking.

This method abstracts away the manual creation of `EventActions` and `state_delta` for most common state update scenarios within callbacks and tools, making your code cleaner and less error-prone.

For more comprehensive details on context objects, refer to the [Context documentation](https://google.github.io/adk-docs/context/index.md).

```python
# In an agent callback or tool function
from google.adk.agents import CallbackContext # or ToolContext

def my_callback_or_tool_function(context: CallbackContext, # Or ToolContext
                                 # ... other parameters ...
                                ):
    # Update existing state
    count = context.state.get("user_action_count", 0)
    context.state["user_action_count"] = count + 1

    # Add new state
    context.state["temp:last_operation_status"] = "success"

    # State changes are automatically part of the event's state_delta
    # ... rest of callback/tool logic ...
```

```typescript
// In an agent callback or tool function
import { CallbackContext } from "@google/adk"; // or ToolContext

function myCallbackOrToolFunction(
    context: CallbackContext, // Or ToolContext
    // ... other parameters ...
) {
    // Update existing state
    const count = context.state.get("user_action_count", 0);
    context.state.set("user_action_count", count + 1);

    // Add new state
    context.state.set("temp:last_operation_status", "success");

    // State changes are automatically part of the event's stateDelta
    // ... rest of callback/tool logic ...
}
```

```go
//  3. contextStateUpdateExample demonstrates the recommended way to modify state
//     from within a tool function using the provided `tool.Context`.
func contextStateUpdateExample(sessionService session.Service) {
    fmt.Println("--- Running Context State Update (ToolContext) Example ---")
    ctx := context.Background()

    // Define the tool that modifies state
    updateActionCountTool, err := functiontool.New(
        functiontool.Config{Name: "update_action_count", Description: "Updates the user action count in the state."},
        func(tctx tool.Context, args struct{}) (struct{}, error) {
            actx, ok := tctx.(agent.CallbackContext)
            if !ok {
                log.Fatalf("tool.Context is not of type agent.CallbackContext")
            }
            s, err := actx.State().Get("user_action_count")
            if err != nil {
                log.Printf("could not get user_action_count: %v", err)
            }
            newCount := 1
            if c, ok := s.(int); ok {
                newCount = c + 1
            }
            if err := actx.State().Set("user_action_count", newCount); err != nil {
                log.Printf("could not set user_action_count: %v", err)
            }
            if err := actx.State().Set("temp:last_operation_status", "success from tool"); err != nil {
                log.Printf("could not set temp:last_operation_status: %v", err)
            }
            fmt.Println("Tool: Updated state via agent.CallbackContext.")
            return struct{}{}, nil
        },
    )
    if err != nil {
        log.Fatalf("Failed to create tool: %v", err)
    }

    // Define an agent that uses the tool
    modelTool, err := gemini.NewModel(ctx, modelID, nil)
    if err != nil {
        log.Fatalf("Failed to create Gemini model for tool agent: %v", err)
    }
    toolAgent, err := llmagent.New(llmagent.Config{
        Name:        "ToolAgent",
        Model:       modelTool,
        Instruction: "Use the update_action_count tool.",
        Tools:       []tool.Tool{updateActionCountTool},
    })
    if err != nil {
        log.Fatalf("Failed to create tool agent: %v", err)
    }

    r, err := runner.New(runner.Config{
        AppName:        appName,
        Agent:          agent.Agent(toolAgent),
        SessionService: sessionService,
    })
    if err != nil {
        log.Fatalf("Failed to create runner: %v", err)
    }

    // Run the agent to trigger the tool
    userMessage := genai.NewContentFromText("Please update the action count.", "user")
    for _, err := range r.Run(ctx, userID, sessionID, userMessage, agent.RunConfig{}) {
        if err != nil {
            log.Printf("Agent Error: %v", err)
        }
    }

    // Check the updated state
    resp, err := sessionService.Get(ctx, &session.GetRequest{AppName: appName, UserID: userID, SessionID: sessionID})
    if err != nil {
        log.Fatalf("Failed to get session: %v", err)
    }
    actionCount, _ := resp.Session.State().Get("user_action_count")
    fmt.Printf("State after tool run: user_action_count = %v\n", actionCount)
}
```

```java
// In an agent callback or tool method
import com.google.adk.agents.CallbackContext; // or ToolContext
// ... other imports ...

public class MyAgentCallbacks {
    public void onAfterAgent(CallbackContext callbackContext) {
        // Update existing state
        Integer count = (Integer) callbackContext.state().getOrDefault("user_action_count", 0);
        callbackContext.state().put("user_action_count", count + 1);

        // Add new state
        callbackContext.state().put("temp:last_operation_status", "success");

        // State changes are automatically part of the event's state_delta
        // ... rest of callback logic ...
    }
}
```

**What `append_event` Does:**

- Adds the `Event` to `session.events`.
- Reads the `state_delta` from the event's `actions`.
- Applies these changes to the state managed by the `SessionService`, correctly handling prefixes and persistence based on the service type.
- Updates the session's `last_update_time`.
- Ensures thread-safety for concurrent updates.

### ⚠️ A Warning About Direct State Modification

Avoid directly modifying the `session.state` collection (dictionary/Map) on a `Session` object that was obtained directly from the `SessionService` (e.g., via `session_service.get_session()` or `session_service.create_session()`) *outside* of the managed lifecycle of an agent invocation (i.e., not through a `CallbackContext` or `ToolContext`). For example, code like `retrieved_session = await session_service.get_session(...); retrieved_session.state['key'] = value` is problematic.

State modifications *within* callbacks or tools using `CallbackContext.state` or `ToolContext.state` are the correct way to ensure changes are tracked, as these context objects handle the necessary integration with the event system.

**Why direct modification (outside of contexts) is strongly discouraged:**

1. **Bypasses Event History:** The change isn't recorded as an `Event`, losing auditability.
1. **Breaks Persistence:** Changes made this way **will likely NOT be saved** by `DatabaseSessionService` or `VertexAiSessionService`. They rely on `append_event` to trigger saving.
1. **Not Thread-Safe:** Can lead to race conditions and lost updates.
1. **Ignores Timestamps/Logic:** Doesn't update `last_update_time` or trigger related event logic.

**Recommendation:** Stick to updating state via `output_key`, `EventActions.state_delta` (when manually creating events), or by modifying the `state` property of `CallbackContext` or `ToolContext` objects when within their respective scopes. These methods ensure reliable, trackable, and persistent state management. Use direct access to `session.state` (from a `SessionService`-retrieved session) only for *reading* state.

### Best Practices for State Design Recap

- **Minimalism:** Store only essential, dynamic data.
- **Serialization:** Use basic, serializable types.
- **Descriptive Keys & Prefixes:** Use clear names and appropriate prefixes (`user:`, `app:`, `temp:`, or none).
- **Shallow Structures:** Avoid deep nesting where possible.
- **Standard Update Flow:** Rely on `append_event`.
