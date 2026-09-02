---
catalog_title: Slack
catalog_description: Run agents as bots that reply to mentions, DMs, and threads
catalog_icon: /integrations/assets/slack.png
catalog_tags: ["connectors"]
---

# Slack runner for ADK

<div class="language-support-tag"><span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span></div>

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
--8<-- "examples/inline/python/integrations/slack/001-use-with-agent.py"
```

## Additional resources

- [Slack API Documentation](https://api.slack.com/docs)
- [google-adk on PyPI](https://pypi.org/project/google-adk/)
