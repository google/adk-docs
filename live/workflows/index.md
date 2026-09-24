# Graph workflows for live agents

Supported in ADKPython v2.0.0

Live agents compose into the same graph workflows as any other ADK agent. Defining nodes and edges, routing, and state are covered in [Graph workflows](https://adk.dev/graphs/index.md), and the broader multi-agent picture in [Workflows](https://adk.dev/workflows/index.md). What changes under a live connection is the execution model.

Under `run_live()`, a whole pipeline of agents runs *inside one open connection and one event loop*, so the caller hears a single continuous conversation. They keep talking while control moves from one agent to the next, and never hear the handoff.

That shapes your code too. With a request/response agent, each agent transition is a fresh call you control; here it is one loop and one queue for the entire workflow, no matter how many agents it spans.

## Run agents in a graph

A graph [`Workflow`](https://adk.dev/graphs/index.md) is how you sequence live agents in ADK 2.0. You define the agents as nodes and connect them with edges, and the runner walks the graph over a single live session:

```python
from google.adk.agents.llm_agent import Agent
from google.adk.workflow import START, Workflow

LIVE_MODEL = 'gemini-live-2.5-flash-native-audio'

greeter = Agent(
    model=LIVE_MODEL,
    name='greeter',
    mode='task',  # required for the node to use the live connection
    instruction='Greet the caller and confirm you are speaking with John Doe. '
    'Ask one question per turn. Complete your task once the name is confirmed.',
)

verifier = Agent(
    model=LIVE_MODEL,
    name='verifier',
    mode='task',
    instruction='Verify the caller by date of birth, then complete your task.',
)

root_agent = Workflow(
    name='intake',
    edges=[
        (START, greeter),
        (greeter, verifier),
    ],
)
```

Serve this with `adk web` and start a live session, or pass it to `Runner.run_live()`. The runner detects a `Workflow` root and drives it over the live connection; you consume one event stream across all nodes. See the runnable [`live_workflow` sample](https://github.com/google/adk-python/tree/main/contributing/samples/live/live_workflow) for a three-stage voice intake flow with typed handoffs and a live eval set.

**Every agent that speaks needs `mode='task'` or `mode='chat'`.** As a node in a workflow, an `LlmAgent` with no `mode` falls back to `single_turn`, which runs outside the live connection and ignores the audio queue entirely, so the caller hears nothing from it. Set the mode explicitly on every node that talks.

Each node opens its own Live API session for the duration of that node, and the workflow's `LiveRequestQueue` is shared across nodes in sequence. A single queue cannot feed two live nodes at once, so keep live nodes on one path rather than fanning out.

## Read one event stream

The stream is continuous across node transitions. Consume it with one loop and one queue, and read `event.author` to tell which agent is speaking.

```python
queue = LiveRequestQueue()

async for event in runner.run_live(
    user_id='user_123',
    session_id='session_456',
    live_request_queue=queue,
):
    if event.content and event.content.parts:
        for part in event.content.parts:
            if part.inline_data and part.inline_data.mime_type.startswith('audio/'):
                await play_audio(part.inline_data.data)
            elif part.text:
                await display_text(f'[{event.author}] {part.text}')
```

Do not open a new `run_live()` loop or a new `LiveRequestQueue` per agent. One loop and one queue serve the whole workflow; user input flows to whichever node is currently active.

## Hand off mid-conversation

A coordinator agent can pass the conversation to a specialist mid-session with `transfer_to_agent`. The handoff happens inside the same `run_live()` loop: ADK closes the coordinator's live connection, opens a fresh one for the specialist, and the user keeps talking.

```text
User: "I need help with billing"
Event: author="coordinator", function_call: transfer_to_agent(agent_name="billing")
Event: author="billing", text="I can help with your billing question..."
```

Transfers start a new Live API session for the target agent, so session-resumption handles from the coordinator do not carry over. To keep transfers on the coordinator's own team, set `disallow_transfer_to_peers` on the sub-agents; a disallowed sibling transfer raises a `ValueError`.

## Legacy workflow agents

Use a graph `Workflow` for new code. `SequentialAgent`, `LoopAgent`, and `ParallelAgent` are **deprecated in favor of `Workflow`** and will be removed in a future release. `LoopAgent` and `ParallelAgent` raise `NotImplementedError` under `run_live()` and will crash a live session, so keep both off any live path.

`SequentialAgent` still runs in live mode. When it does, ADK adds a `task_completed` tool to each direct `LlmAgent` sub-agent and appends an instruction telling the model to call it when the task is done. Calling `task_completed` ends that sub-agent's live connection and advances to the next agent in the sequence.

```python
# ADK injects this into each LlmAgent sub-agent at live-run time.
def task_completed():
    """Signals that the agent has completed the user's task."""
    return 'Task completion signaled.'
```

The event stream looks like any live workflow: a run of events per agent, then a `task_completed` function response, then the next agent begins:

```text
Event: author="researcher", function_call: task_completed()
Event: author="writer", text="Based on the research..."
```

`task_completed` and `transfer_to_agent` end an agent's turn for different reasons:

| Function            | Pattern         | Effect                                                                    |
| ------------------- | --------------- | ------------------------------------------------------------------------- |
| `task_completed`    | Fixed sequence  | Ends the current agent; the next agent in the sequence begins             |
| `transfer_to_agent` | Dynamic routing | Closes the current live session; a new session opens for the target agent |
