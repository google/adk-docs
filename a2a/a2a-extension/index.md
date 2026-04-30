# A2A extension for improved reliability

Supported in ADKPython 1.27.0

ADK provides an extension for Agent2Agent (A2A) support to improved message and data handling as part of an updated [A2aAgentExecutor](https://github.com/google/adk-python/blob/main/src/google/adk/a2a/executor/a2a_agent_executor_impl.py) class. The updated version includes updates to architectural changes to the core agent execution logic and extensions for A2A to improve data handling, while also providing backward compatibility with existing A2A agents.

Activating the A2A extension option instructs the server to use the updated agent executor implementation. While this update offers several general advantages, it primarily resolves critical limitations found in the legacy A2A-ADK implementation when both A2A and ADK operate in streaming mode. The new implementation addresses the following issues:

- **Message duplication:** Prevents user messages from being duplicated in the task history.
- **Output misclassification:** Stops remote agent ADK outputs from being incorrectly converted into event thoughts.
- **Sub-agent data loss:** Ensures ADK outputs from remote agents are reliably preserved, eliminating data loss when multiple agents are nested within the remote agent's sub-agent tree.

## Client-side extension activation

Clients indicate their desire to use this extension by specifying it via the transport-defined [A2A extension](https://a2a-protocol.org/latest/topics/extensions/) activation mechanism. For JSON-RPC and HTTP transports, this is indicated via the X-A2A-Extensions HTTP header. For gRPC, this is indicated via the X-A2A-Extensions metadata value.

To activate the extension, the client can instantiate the `RemoteA2aAgent` with `use_legacy=False`. This will add `https://google.github.io/adk-docs/a2a/a2a-extension/` among the requested extensions of the sent request. Activating this extension implies that the server will use the new agent executor implementation.

```python
from google.adk.agents import RemoteA2aAgent

remote_agent = RemoteA2aAgent(
    name="remote_agent",
    url="http://localhost:8000/a2a/remote_agent",
    use_legacy=False,
)
```

The `A2aAgentExecutor` uses by default the new implementation, if the a2a extension is detected in the request. To opt-out the new agent executor implementation, the client can simply not send this extension (instantiating the `RemoteA2aAgent` with `use_legacy=True`) or the server's `A2aAgentExecutor` can be instantiated with `use_legacy=True`.

## How it Works

Upon receiving the request, the [A2aAgentExecutor](https://github.com/google/adk-python/blob/main/src/google/adk/a2a/executor/a2a_agent_executor.py) detects the extension. It understands that the client is requesting to use the new agent executor logic and routes the request to the new implementation accordingly. To confirm that the request was honored, it is then included in the "activated extensions" list within the response metadata sent back to the client, as well as in the metadata of the A2A Events.

## Agent Card definition

Agents advertise this extension capability in their AgentCard within the AgentCapabilities.extensions list.

Example AgentExtension block:

```json
{
  "uri": "https://google.github.io/adk-docs/a2a/a2a-extension/",
  "description": "Ability to use the new agent executor implementation",
  "required": false
}
```
