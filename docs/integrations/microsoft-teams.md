---
catalog_title: Microsoft Teams
catalog_description: Run agents as bots in personal chats, group chats, and channels
catalog_icon: /integrations/assets/microsoft-teams.png
catalog_tags: ["connectors"]
---

# Microsoft Teams runner for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v2.14.0</span><span class="lst-preview">Experimental</span>
</div>

ADK provides the `TeamsRunner` class to run your agents as bots in
[Microsoft Teams](https://www.microsoft.com/microsoft-teams). It connects an
ADK `Runner` to an `AgentApplication` from the
[Microsoft 365 Agents SDK](https://learn.microsoft.com/microsoft-365/agents-sdk/),
the successor to the Bot Framework SDK. Teams delivers each message to an HTTPS
endpoint that you host. The runner serves that endpoint, passes the message
text to your agent, and posts the agent's text responses back to the same
conversation.

To send one-way notifications to a channel, a Teams Workflows webhook is
simpler and does not need a bot registration. The
[`teams_notification_agent` sample](https://github.com/google/adk-python/tree/main/contributing/samples/integrations/teams_notification_agent)
shows that approach.

!!! example "Experimental"
    This feature is experimental and may be updated in future releases.

## Use cases

- **Chat with an agent in Teams**: Let users talk to your agent in personal
  chats, group chats, and channel threads, with the bot's `@mention` removed
  from the message.
- **Per-conversation context**: Keep one ADK session per user and conversation,
  so each channel thread has its own history.
- **Long agent turns**: Run model and tool calls that take longer than the
  15 seconds Teams waits for a response, without duplicate runs.

## Prerequisites

- An [Azure Bot](https://learn.microsoft.com/azure/bot-service/abs-quickstart)
  resource with a single tenant Microsoft Entra app registration and a client
  secret.
- The Microsoft Teams channel enabled on the Azure Bot.
- A public HTTPS URL for your server, set as the messaging endpoint of the
  Azure Bot, followed by `/api/messages`.

## Installation

Run the following command to install ADK with the Microsoft 365 Agents SDK
dependencies:

```bash
pip install "google-adk[teams]"
```

## Use with agent

The following example builds an agent, wraps it in an `AgentApplication`
configured from environment variables, and serves the Teams endpoint at
`http://localhost:3978/api/messages`.

```python
import asyncio
import os

from google.adk.agents import Agent
from google.adk.integrations.teams import TeamsRunner
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from microsoft_agents.activity import load_configuration_from_env
from microsoft_agents.authentication.msal import MsalConnectionManager
from microsoft_agents.hosting.aiohttp import CloudAdapter
from microsoft_agents.hosting.core import AgentApplication
from microsoft_agents.hosting.core import MemoryStorage
from microsoft_agents.hosting.core import TurnState

root_agent = Agent(
    model="gemini-flash-latest",
    name="teams_agent",
    instruction="You are a helpful team assistant running on Microsoft Teams.",
)


async def main():
    runner = Runner(
        app_name="teams_agent",
        agent=root_agent,
        session_service=InMemorySessionService(),
        auto_create_session=True,
    )

    sdk_config = load_configuration_from_env(os.environ)
    connection_manager = MsalConnectionManager(**sdk_config)
    agent_app = AgentApplication[TurnState](
        storage=MemoryStorage(),
        adapter=CloudAdapter(connection_manager=connection_manager),
        connection_manager=connection_manager,
        **sdk_config,
    )

    teams_runner = TeamsRunner(runner=runner, agent_app=agent_app)
    await teams_runner.start(
        connection_manager.get_default_connection_configuration()
    )


asyncio.run(main())
```

The `Runner` needs `auto_create_session=True`, because `TeamsRunner` picks the
session ID for each conversation and does not create sessions itself.

## Configuration

The `load_configuration_from_env` call reads the bot registration from these
environment variables:

```bash
export CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID="{app id}"
export CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTSECRET="{client secret}"
export CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID="{tenant id}"
```

Anyone with the client secret can send messages as the bot, so load it from a
secret store such as [Secret Manager](/integrations/secret-manager/) in
production.

The `TeamsRunner` class takes two keyword arguments:

| Option | Type | Description |
| :--- | :--- | :--- |
| `runner` | `Runner` | The ADK runner that executes the agent. |
| `agent_app` | `AgentApplication[TurnState]` | The Microsoft 365 Agents SDK application that receives Teams activities. It must use an aiohttp `CloudAdapter`. |

The `start` method serves the endpoint until it is cancelled:

| Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `auth_configuration` | `AgentAuthConfiguration` | Required | Settings used to validate the token on each incoming request. |
| `host` | `str` | `"localhost"` | The interface to listen on. Use `"0.0.0.0"` in a container. |
| `port` | `int` | `3978` | The port to listen on. |

### Test locally without a registration

For local development, the
[Microsoft 365 Agents Playground](https://www.npmjs.com/package/@microsoft/teams-app-test-tool)
sends Teams-style activities to your endpoint without a bot registration. Set
`CONNECTIONS__SERVICE_CONNECTION__SETTINGS__ANONYMOUS_ALLOWED=True`, leave the
other connection settings unset, and run `teamsapptester`. Do not allow
anonymous access on a server that is reachable from the internet, because it
lets anyone send messages to the agent.

### Mount the endpoint in your own server

The `create_app` method returns the aiohttp application that `start` would
serve. Use it when the endpoint shares a server with other routes:

```python
from aiohttp import web

app = web.Application()
app.add_subapp(
    "/teams",
    teams_runner.create_app(
        connection_manager.get_default_connection_configuration()
    ),
)
web.run_app(app, host="0.0.0.0", port=8080)
```

With the sub-application mounted at `/teams`, the messaging endpoint to
register in Azure is `https://{your host}/teams/api/messages`.

## How it works

- **Sessions**: The session ID is derived from the Teams conversation ID. A
  personal chat and a group chat each have one conversation, and each channel
  thread has its own. The user ID is the sender's Microsoft Entra object ID, so
  two people in the same channel thread each get their own session.
- **Background replies**: Teams retries any request that takes longer than
  15 seconds. The runner acknowledges each message right away, runs the
  agent in the background, and shows a typing indicator while it works.
  Messages for the same session run one at a time, in order.
- **Responses**: Each non-thought text part of a final event is posted as its
  own message. If the run fails, the user gets a generic error message and the
  exception is logged, not sent to Teams.

## Limitations

- **Text only**: Attachments, images, and Adaptive Card submissions are not
  passed to the agent, and the agent's non-text output is not posted to Teams.
- **In-process runs**: If the server process stops during a run, the reply is
  lost. On platforms that throttle CPU between requests, such as Cloud Run with
  request-based billing, keep CPU allocated outside requests.
- **Session storage**: With `InMemorySessionService`, history is lost on
  restart and is not shared across replicas. Use a persistent service such as
  `DatabaseSessionService` or `VertexAiSessionService` when you run more than
  one instance. See [Sessions](/sessions/session/).

## Additional resources

- [TeamsRunner guide in ADK Python](https://github.com/google/adk-python/blob/main/docs/guides/integrations/teams/teams_runner/index.md)
- [`teams_agent` sample](https://github.com/google/adk-python/tree/main/contributing/samples/integrations/teams_agent)
- [Microsoft 365 Agents SDK documentation](https://learn.microsoft.com/microsoft-365/agents-sdk/)
- [google-adk on PyPI](https://pypi.org/project/google-adk/)
