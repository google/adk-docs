# Run agents in code

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-java">Java v0.1.0</span>
</div>

In addition to the Dev UI, CLI, and API server, you can run ADK agents
directly from your own code. This is useful for integrating agents into
existing applications, building custom interfaces, running automated
pipelines, and writing tests.

ADK provides two main approaches:

- **`run_debug()`**: A convenience method for quick experimentation. It
  handles session creation and message formatting automatically.
- **`run_async()`**: The full-control method for production use. It gives you
  explicit control over sessions, message formatting, event streaming, and
  runtime configuration.

## Quick start with `run_debug()`

The fastest way to invoke an agent from code is with `InMemoryRunner.run_debug()`.
This method creates a session, sends a user message, and collects all response
events automatically.

!!! note "Version requirement"

    `run_debug()` requires ADK Python v1.18.0 or higher.

=== "Python"

    ```python title="main.py"
    import asyncio
    from google.adk.agents import Agent
    from google.adk.runners import InMemoryRunner

    # 1. Define your agent
    agent = Agent(
        name="greeting_agent",
        model="gemini-flash-latest",
        description="A friendly greeting agent.",
        instruction="Greet the user warmly and ask how you can help.",
    )

    # 2. Create a runner
    runner = InMemoryRunner(agent=agent, app_name="my_app")

    # 3. Run the agent and collect events
    async def main():
        events = await runner.run_debug("Hello there!")
        for event in events:
            if event.is_final_response():
                print(event.content.parts[0].text)

    if __name__ == "__main__":
        asyncio.run(main())
    ```

`run_debug()` returns a `list[Event]` — the complete sequence of events the
agent produced in response to your message. You can inspect these events to
find the final text response, tool calls, state changes, and more. For
details on the event structure, see [Events](../events/index.md).

### Using `run_debug()` with an App

If your agent is configured through an [App](../apps/index.md) object, pass
it to `InMemoryRunner` using the `app` parameter:

=== "Python"

    ```python title="main.py"
    import asyncio
    from dotenv import load_dotenv
    from google.adk.runners import InMemoryRunner
    from agent import app  # import your App object

    load_dotenv()  # load API keys and settings
    runner = InMemoryRunner(app=app)

    async def main():
        events = await runner.run_debug("Hello there!")
        for event in events:
            if event.is_final_response():
                print(event.content.parts[0].text)

    if __name__ == "__main__":
        asyncio.run(main())
    ```

## Full control with `run_async()`

For production applications, use `run_async()` to get full control over
session management, message formatting, and event streaming. This method
is available on both `Runner` and `InMemoryRunner`.

### Using `InMemoryRunner`

`InMemoryRunner` uses in-memory session and artifact services, so you don't
need to configure external storage. This is the easiest way to use
`run_async()`:

=== "Python"

    ```python title="main.py"
    import asyncio
    from google.adk.agents import Agent
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    # Define your agent
    agent = Agent(
        name="weather_agent",
        model="gemini-flash-latest",
        description="Agent to answer questions about weather.",
        instruction="You are a helpful weather assistant.",
    )

    app_name = "weather_app"
    user_id = "test_user"
    session_id = "test_session"

    runner = InMemoryRunner(agent=agent, app_name=app_name)

    async def main():
        # Create a session
        session = await runner.session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )

        # Build the user message
        user_message = types.Content(
            role="user",
            parts=[types.Part(text="What is the weather in New York?")],
        )

        # Stream events from the agent
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_message,
        ):
            if event.is_final_response():
                print(event.content.parts[0].text)

    if __name__ == "__main__":
        asyncio.run(main())
    ```

=== "TypeScript"

    ```typescript title="main.ts"
    import {
      InMemoryRunner,
      LlmAgent,
    } from '@google/adk';

    const agent = new LlmAgent({
      name: 'weather_agent',
      model: 'gemini-flash-latest',
      description: 'Agent to answer questions about weather.',
      instruction: 'You are a helpful weather assistant.',
    });

    const runner = new InMemoryRunner({
      agent,
      appName: 'weather_app',
    });

    const userId = 'test_user';
    const sessionId = 'test_session';

    // Create a session
    await runner.sessionService.createSession({
      appName: 'weather_app',
      userId,
      sessionId,
    });

    // Stream events from the agent
    for await (const event of runner.runAsync({
      userId,
      sessionId,
      newMessage: {
        role: 'user',
        parts: [{ text: 'What is the weather in New York?' }],
      },
    })) {
      if (event.isFinalResponse()) {
        console.log(event.content?.parts?.[0]?.text);
      }
    }
    ```

=== "Java"

    ```java title="Main.java"
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.runner.InMemoryRunner;
    import com.google.genai.types.Content;
    import com.google.genai.types.Part;

    public class Main {
      public static void main(String[] args) throws Exception {
        LlmAgent agent = LlmAgent.builder()
            .name("weather_agent")
            .model("gemini-flash-latest")
            .description("Agent to answer questions about weather.")
            .instruction("You are a helpful weather assistant.")
            .build();

        InMemoryRunner runner = new InMemoryRunner(agent);
        String userId = "test_user";
        String sessionId = "test_session";

        runner.sessionService()
            .createSession("weather_app", userId, null, sessionId)
            .blockingGet();

        runner.runAsync(
                userId,
                sessionId,
                Content.fromParts(Part.fromText("What is the weather in New York?"))
            )
            .filter(event -> event.finalResponse() && event.content().isPresent())
            .blockingSubscribe(event ->
                System.out.println(event.stringifyContent())
            );
      }
    }
    ```

### Using `Runner` with custom services

For full control over storage and services, use the `Runner` class directly.
This lets you plug in custom `SessionService`, `ArtifactService`, and
`MemoryService` implementations:

=== "Python"

    ```python title="main.py"
    import asyncio
    from google.adk.agents import Agent
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.adk.artifacts import InMemoryArtifactService
    from google.genai import types

    # Define your agent
    agent = Agent(
        name="support_agent",
        model="gemini-flash-latest",
        description="A customer support agent.",
        instruction="Help the user with their questions.",
    )

    # Configure services
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()

    # Create a Runner with custom services
    runner = Runner(
        agent=agent,
        app_name="support_app",
        session_service=session_service,
        artifact_service=artifact_service,
    )

    async def main():
        # Create a session
        session = await session_service.create_session(
            app_name="support_app",
            user_id="user_123",
            session_id="session_001",
        )

        # Build the user message
        user_message = types.Content(
            role="user",
            parts=[types.Part(text="I need help with my account.")],
        )

        # Stream events from the agent
        async for event in runner.run_async(
            user_id="user_123",
            session_id="session_001",
            new_message=user_message,
        ):
            if event.is_final_response():
                print(event.content.parts[0].text)

    if __name__ == "__main__":
        asyncio.run(main())
    ```

### Using `RunConfig`

You can pass a `RunConfig` to `run_async()` to configure runtime behavior
such as streaming mode and LLM call limits:

=== "Python"

    ```python
    from google.adk.agents.run_config import RunConfig, StreamingMode

    config = RunConfig(
        streaming_mode=StreamingMode.SSE,
        max_llm_calls=200,
    )

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=user_message,
        run_config=config,
    ):
        ...
    ```

For a complete list of `RunConfig` options, see [Runtime Config](runconfig.md).

## Choosing the right approach

| Approach | Best for | Session management | Event streaming |
|---|---|---|---|
| `run_debug()` | Quick prototyping, testing, scripts | Automatic | Returns `list[Event]` |
| `InMemoryRunner.run_async()` | Development, integration tests | Manual (in-memory) | `async for` streaming |
| `Runner.run_async()` | Production apps, custom storage | Manual (pluggable services) | `async for` streaming |

## Related topics

- **[Events](../events/index.md)**: Understand the event structure returned by
  agent runs.
- **[Runtime Config](runconfig.md)**: Configure runtime behavior with
  `RunConfig`.
- **[Event Loop](event-loop.md)**: Understand the core event loop that powers
  ADK.
- **[App management](../apps/index.md)**: Use the `App` class for lifecycle
  management and configuration.
