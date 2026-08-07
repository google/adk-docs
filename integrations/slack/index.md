# Slack runner for ADK

Supported in ADKPython

ADK provides the `SlackRunner` class to allow you to deploy your agents directly on Slack using [Socket Mode](https://api.slack.com/apis/connections/socket). This integration acts as an adapter that handles event listening, response dispatching, and automated conversation thread management.

## Use cases

- **Socket Mode deployment**: Route workspace events to your agent without exposing public HTTP endpoints.
- **Thread management**: Maintain continuous conversation context across direct messages and nested thread replies.
- **Event-driven triggers**: Activate agent workflows automatically using direct messages or app mentions.

## Prerequisites

- Slack App configured in your [Slack API Dashboard](https://api.slack.com/apps). You must sign in to your Slack account first.
- Bot User OAuth Token (`xoxb-...`) with `app_mentions:read`, `chat:write`, and `im:history` bot token scopes.
- Websocket App-Level Token (`xapp-...`) with the `connections:write` scope.

## Installation

Run the following command in your terminal to install the ADK along with all necessary Slack Socket Mode dependencies

```bash
pip install "google-adk[slack]"
```

## Use with agent

This example shows you the end-to-end setup for deploying an agent to Slack. It configures a core agent, establishes an in-memory session to manage conversation history, and uses SlackRunner with Socket Mode to connect to your workspace and handle incoming events.

```python
import asyncio
import os
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.integrations.slack import SlackRunner
from slack_bolt.app.async_app import AsyncApp

# Define the core agent
root_agent = Agent(
    model="gemini-flash-latest",
    name="slack_agent",
    instruction="You are a helpful team assistant running on Slack.",
)

# Wire it up to Slack over Socket Mode
runner = Runner(
    app_name="slack_agent",
    agent=root_agent,
    session_service=InMemorySessionService(),
    auto_create_session=True,
)
slack_app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])
slack_runner = SlackRunner(runner, slack_app)

asyncio.run(slack_runner.start(os.environ["SLACK_APP_TOKEN"]))
```

## Additional resources

- [Slack API Documentation](https://api.slack.com/docs)
- [google-adk on PyPI](https://pypi.org/project/google-adk/)
