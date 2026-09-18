---
catalog_title: LiveKit
catalog_description: Put a live voice agent in a WebRTC room or on a phone call
catalog_icon: /integrations/assets/livekit.png
catalog_tags: ["connectors"]
---

# LiveKit runner for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v2.9.0</span><span class="lst-preview">Experimental</span>
</div>

ADK provides the `LiveKitRunner` class to allow you to serve your live agents over
[LiveKit](https://livekit.io/), an open source platform for WebRTC and SIP telephony. This
integration acts as a transport adapter that handles audio and video capture, playback,
barge-in, captions, and call control, so your ADK agent can become reachable from a browser,
a phone, or a game client without any change to the agent.

## Use cases

### Browser and mobile apps

The agent joins a room as an ordinary participant, so any LiveKit client SDK can talk to it.
The connector publishes captions and speaking state on the channels LiveKit's own
components bind to, so most of a voice front end already exists:

| LiveKit resource | What an ADK agent gets |
| :--- | :--- |
| [Client SDKs](https://docs.livekit.io/transport/) | Browser, Swift, Android, Flutter, React Native, Unity, C++, Rust, and ESP32 |
| [UI components](https://github.com/orgs/livekit/repositories?q=components) | Prebuilt voice-assistant widgets for React, SwiftUI, Compose, and Flutter |
| [Starter apps](https://github.com/livekit-examples) | Working apps per platform, plus the Agents Playground for talking to an agent with no front end at all |

### Phone calls

A SIP caller is an ordinary LiveKit participant, so a phone call reaches the agent once an
[inbound trunk](https://docs.livekit.io/telephony/accepting-calls/inbound-trunk/) and a
[dispatch rule](https://docs.livekit.io/telephony/accepting-calls/dispatch-rule/) point at
your worker.

Caller identity lands in ADK session state before the caller speaks, so a function tool reads
it like any other state value:

```python
from google.adk.tools.tool_context import ToolContext

async def greet_by_account(tool_context: ToolContext) -> str:
  """Looks the caller up before greeting them."""
  number = tool_context.state.get("livekit_caller_phone_number")  # '+15105550100'
  if not number:
    return "I could not see the number you are calling from."
  return await crm.lookup(number)  # your own customer lookup
```

The connector buffers keypad entry into a single turn, so a six-digit account number arrives
as one input instead of six interruptions.

### Games and immersive clients

LiveKit's [Unity SDK](https://github.com/livekit/client-sdk-unity) adds realtime audio,
video, and data channels to a Unity app, backed by LiveKit Cloud or a server you host. Put an
ADK agent in the room and a player can hold a conversation with a character that also acts
on the world, such as a voice-driven NPC or an in-game assistant:

```python
from google.adk.integrations.livekit import current_call
from google.adk.tools.tool_context import ToolContext

async def open_the_door(door_id: str, tool_context: ToolContext) -> str:
  """Opens a door in the game world."""
  call = current_call(tool_context)
  return await call.perform_rpc(method="open_door", payload=door_id)
```

Whatever the client returns becomes the tool result the model narrates, so the agent
describes what actually happened. The Unity side is one registered RPC method, and ADK keeps
the conversation, the tool calls, and the session.

## Get started

- [ADK](https://adk.dev) >= 2.9.0 with the `livekit` extra.
- Credentials for a [live model](../live/models.md).
- A LiveKit server, self-hosted or on LiveKit Cloud. Both expose the same API, so the
  choice is operational. For local development, run `livekit-server --dev`.
- `LIVEKIT_URL`, `LIVEKIT_API_KEY`, and `LIVEKIT_API_SECRET` set in the environment.

```bash
pip install "google-adk[livekit]" "livekit-agents>=1.4"
```

Start from the agent you already have. Adding `LiveKitToolset()` gives it call controls such
as hanging up or transferring a caller. The toolset activates only when there is a call, so
`adk web` still runs the agent unchanged:

```python
from google.adk.agents import Agent
from google.adk.integrations.livekit import LiveKitToolset
from google.adk.runners import InMemoryRunner

root_agent = Agent(
    model="gemini-live-2.5-flash-native-audio",
    name="support_agent",
    instruction="You help customers troubleshoot their home internet.",
    tools=[check_line_status, LiveKitToolset()],  # check_line_status is your own tool
)
runner = InMemoryRunner(agent=root_agent, app_name="support")
```

Handing that runner a connected room is the whole integration. In production you run a
worker, which LiveKit dispatches once per call, and the same code serves a browser and a
phone.

```python
from google.adk.integrations.livekit import LiveKitRunner
from livekit.agents import AgentServer
from livekit.agents import cli
from livekit.agents import JobContext

server = AgentServer()


@server.rtc_session(agent_name="support")
async def entrypoint(ctx: JobContext) -> None:
  """Bridges one dispatched call into the ADK agent."""
  await ctx.connect()
  # LiveKit has no ADK user or session ids. The sample reads them from job metadata.
  await LiveKitRunner(
      runner=runner, room=ctx.room, user_id="live-user", session_id=ctx.room.name
  ).start()


if __name__ == "__main__":
  cli.run_app(server)
```

## Deploy the worker

The worker dials out to the LiveKit server and receives dispatched jobs over that same
connection, so it needs outbound network access, no public address, and no load balancer.
Otherwise it is a normal ADK container and deploys the way any ADK agent does. Point the
entrypoint at your worker module:

```dockerfile
CMD ["python", "-m", "support_agent.livekit_worker", "start"]
```

[Agents CLI](../get-started/agents-cli.md) deploys that container to Agent Runtime, Cloud
Run, or GKE from the `deployment_target` in your `pyproject.toml`. See
[Deploy with Agents CLI](../deploy/agent-runtime/agents-cli.md), or deploy by hand to
[Cloud Run](../deploy/cloud-run.md) or [GKE](../deploy/gke.md).

Cloud Run probes `$PORT`, while the worker serves its health endpoint on a fixed port, so
make the two match. Read the port from the environment when you create the server:

```python
import os

server = AgentServer(port=int(os.environ["PORT"]))
```

Deploying with `--port=8081` does the same job, since that is the port the worker uses in
production. The worker also sits idle between calls, so run with `--no-cpu-throttling` and
`--min-instances=1` to keep it accepting dispatch.

Each dispatched job runs in its own process, so use a durable
[session service](../sessions/index.md). The `InMemoryRunner` class persists nothing
between calls.

## Additional resources

- [LiveKit sample](https://github.com/google/adk-python/tree/main/contributing/samples/integrations/livekit)
- [Live and voice agents](../live/index.md)
- [Build a custom server](../live/custom-server.md)
- [LiveKit documentation](https://docs.livekit.io/)
