# Workflows

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.5.0</span><span class="lst-preview">Experimental</span>
</div>

Multi-agent workflows behave differently under a live connection. With a request/response
agent, each agent transition is a fresh call you control. Under `run_live()`, a
`SequentialAgent` pipeline or a coordinator handing off to a specialist all happens
*inside a single open connection and a single event loop* — the transitions are invisible
to your code, and the user keeps talking through them.

That changes what correct application code looks like: one loop, one queue, for the whole
workflow. This page covers the patterns that hold up and the ones that break.

## Best Practices for Multi-Agent Workflows

ADK's bidirectional streaming supports three agent architectures: **single agent** (one agent handles the entire conversation), **multi-agent with sub-agents** (a coordinator agent dynamically routes to specialist agents using `transfer_to_agent`), and **sequential workflow agents** (agents execute in a fixed pipeline using `task_completed`). This section focuses on best practices for sequential workflows, where understanding agent transitions and state sharing is crucial for smooth bidirectional communication.

!!! note "Learn More"

    For comprehensive coverage of multi-agent patterns, see [Workflows](../workflows/index.md) in the ADK documentation.

When building multi-agent systems with ADK, understanding how agents transition and share state during live streaming is crucial for smooth bidirectional communication.

### SequentialAgent with Bidi-streaming

`SequentialAgent` enables workflow pipelines where agents execute one after another. Each agent completes its task before the next one begins. The challenge with live streaming is determining when an agent has finished processing continuous audio or video input.

!!! note "Reference"

    [`SequentialAgent`](../api-reference/python/google-adk.html#google.adk.agents.SequentialAgent) in the Python API reference

**How it works:**

ADK automatically adds a `task_completed()` function to each agent in the sequence. When the model calls this function, it signals completion and triggers the transition to the next agent:

**Usage:**

```python
# SequentialAgent automatically adds this tool to each sub-agent
def task_completed():
    """
    Signals that the agent has successfully completed the user's question
    or task.
    """
    return 'Task completion signaled.'
```

### Recommended Pattern: Transparent Sequential Flow

The key insight is that **agent transitions happen transparently** within the same `run_live()` event stream. Your application doesn't need to manage transitions—just consume events uniformly:

**Usage:**

```python
async def handle_sequential_workflow():
    """Recommended pattern for SequentialAgent with bidi-streaming."""

    # 1. Single queue shared across all agents in the sequence
    queue = LiveRequestQueue()

    # 2. Background task captures user input continuously
    async def capture_user_input():
        while True:
            # Your logic to read audio from microphone
            audio_chunk = await microphone.read()
            queue.send_realtime(
                blob=types.Blob(data=audio_chunk, mime_type="audio/pcm")
            )

    input_task = asyncio.create_task(capture_user_input())

    try:
        # 3. Single event loop handles ALL agents seamlessly
        async for event in runner.run_live(
            user_id="user_123",
            session_id="session_456",
            live_request_queue=queue,
        ):
            # Events flow seamlessly across agent transitions
            current_agent = event.author

            # Handle audio and text output
            if event.content and event.content.parts:
                for part in event.content.parts:
                    # Check for audio data
                    if part.inline_data and part.inline_data.mime_type.startswith("audio/"):
                        # Your logic to play audio
            await play_audio(part.inline_data.data)

                    # Check for text data
                    if part.text:
                        await display_text(f"[{current_agent}] {part.text}")

            # No special transition handling needed!

    finally:
        input_task.cancel()
        queue.close()
```

### Event Flow During Agent Transitions

Here's what your application sees when agents transition:

```text
# Agent 1 (Researcher) completes its work
Event: author="researcher", text="I've gathered all the data."
Event: author="researcher", function_call: task_completed()
Event: author="researcher", function_response: task_completed

# --- Automatic transition (invisible to your code) ---

# Agent 2 (Writer) begins
Event: author="writer", text="Let me write the report based on the research..."
Event: author="writer", text=" The findings show..."
Event: author="writer", function_call: task_completed()
Event: author="writer", function_response: task_completed

# --- Automatic transition ---

# Agent 3 (Reviewer) begins - the last agent in sequence
Event: author="reviewer", text="Let me review the report..."
Event: author="reviewer", text="The report looks good. All done!"
Event: author="reviewer", function_call: task_completed()
Event: author="reviewer", function_response: task_completed

# --- Last agent completed: run_live() exits ---
# Your async for loop ends here
```

### Design Principles

#### 1. Single Event Loop

Use one event loop for all agents in the sequence:

**Usage:**

```python
# ✅ CORRECT: One loop handles all agents
async for event in runner.run_live(...):
    # Your event handling logic here
    await handle_event(event)  # Works for Agent1, Agent2, Agent3...

# ❌ INCORRECT: Don't break the loop or create multiple loops
for agent in agents:
    async for event in runner.run_live(...):  # WRONG!
        ...
```

#### 2. Persistent Queue

The same `LiveRequestQueue` serves all agents:

```text
# User input flows to whichever agent is currently active
User speaks → Queue → Agent1 (researcher)
                ↓
User speaks → Queue → Agent2 (writer)
                ↓
User speaks → Queue → Agent3 (reviewer)
```

**Don't create new queues per agent:**

```python
# ❌ INCORRECT: New queue per agent
for agent in agents:
    new_queue = LiveRequestQueue()  # WRONG!

# ✅ CORRECT: Single queue for entire workflow
queue = LiveRequestQueue()
async for event in runner.run_live(live_request_queue=queue):
    ...
```

#### 3. Agent-Aware UI (Optional)

Track which agent is active for better user experience:

**Usage:**

```python
current_agent_name = None

async for event in runner.run_live(...):
    # Detect agent transitions
    if event.author and event.author != current_agent_name:
        current_agent_name = event.author
        # Your logic to update UI indicator
        await update_ui_indicator(f"Now: {current_agent_name}")

    # Your event handling logic here
    await handle_event(event)
```

#### 4. Transition Notifications

Optionally notify users when agents hand off:

**Usage:**

```python
async for event in runner.run_live(...):
    # Detect task completion (transition signal)
    if event.content and event.content.parts:
        for part in event.content.parts:
            if (part.function_response and
                part.function_response.name == "task_completed"):
                # Your logic to display transition notification
                await display_notification(
                    f"✓ {event.author} completed. Handing off to next agent..."
                )
                continue

    # Your event handling logic here
    await handle_event(event)
```

### Key Differences: transfer_to_agent vs task_completed

Understanding these two functions helps you choose the right multi-agent pattern:

| Function | Agent Pattern | When `run_live()` Exits | Use Case |
|----------|--------------|----------------------|----------|
| `transfer_to_agent` | Coordinator (dynamic routing) | `LiveRequestQueue.close()` | Route user to specialist based on intent |
| `task_completed` | Sequential (pipeline) | `LiveRequestQueue.close()` or `task_completed` of the last agent | Fixed workflow: research → write → review |

**transfer_to_agent example:**

```text
# Coordinator routes based on user intent
User: "I need help with billing"
Event: author="coordinator", function_call: transfer_to_agent(agent_name="billing")
# Stream continues with billing agent - same run_live() loop
Event: author="billing", text="I can help with your billing question..."
```

**task_completed example:**

```text
# Sequential workflow progresses through pipeline
Event: author="researcher", function_call: task_completed()
# Current agent exits, next agent in sequence begins
Event: author="writer", text="Based on the research..."
```

### Best Practices Summary

| Practice | Reason |
|----------|--------|
| Use single event loop | ADK handles transitions internally |
| Keep queue alive across agents | Same queue serves all sequential agents |
| Track `event.author` | Know which agent is currently responding |
| Don't reset session/context | Conversation state persists across agents |
| Handle events uniformly | All agents produce the same event types |
| Let `task_completed` signal transitions | Don't manually manage sequential flow |

The SequentialAgent design ensures smooth transitions—your application simply sees a continuous stream of events from different agents in sequence, with automatic handoffs managed by ADK.

