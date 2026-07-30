---
catalog_title: Slack
catalog_description: Deploy ADK agents directly to Slack using Socket Mode.
catalog_icon: /integrations/assets/slack-runner.png
catalog_tags: ["runner", "slack"]
---

# Slack runner for ADK

<div class="language-support-tag"><span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span></div>

ADK provides the `SlackRunner` class to easily deploy your agents directly on Slack using [Socket Mode](https://api.slack.com/apis/connections/socket). This integration acts as an adapter that handles event listening, response dispatching, and automated conversation thread management.

## Use cases

- **Socket Mode deployment**: Route workspace events securely to your agent without exposing public HTTP endpoints.
- **Thread management**: Maintain continuous conversation context across direct messages and nested thread replies.
- **Event-driven triggers**: Activate agent workflows automatically using direct messages or app mentions.

## Prerequisites

- A Slack App configured in your [Slack API Dashboard](https://api.slack.com/apps). You must sign in to your Slack account first.
- A **Bot User OAuth Token** (`xoxb-...`) with `app_mentions:read`, `chat:write`, and `im:history` bot token scopes.
- A **Websocket App-Level Token** (`xapp-...`) with the `connections:write` scope.

## Installation

```bash
pip install "google-adk[slack]"
```

## Use with agent

```python
import asyncio
import os
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.integrations.slack import SlackRunner
from slack_bolt.app.async_app import AsyncApp

# Define the core agent
root_agent = Agent(
    model="gemini-flash-latest",
    name="slack_agent",
    instruction="You are a helpful team assistant running on Slack.",
)
```

## Available tools

Tool | Description
------ | -----------
`__init__(runner, slack_app)` | Starts the Slack runner adapter with an ADK `Runner` and a Slack `AsyncApp`.
`start(app_token)` | Starts the Slack runner listener in Socket Mode using your app-level websocket token.

## Additional resources

- [Slack API Documentation](https://api.slack.com/docs)
- [google-adk on PyPI](https://pypi.org/project/google-adk/)
