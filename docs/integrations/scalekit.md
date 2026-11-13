---
catalog_title: Scalekit
catalog_description: Per-user authenticated tools across 500+ apps, with scoped access and audit logs
catalog_icon: /integrations/assets/scalekit.png
catalog_tags: ["connectors", "mcp"]
---

# Scalekit

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Scalekit](https://www.scalekit.com) is an agent integration platform that lets
your ADK agent act in third-party apps on behalf of each of your users. A user
authorizes Gmail, Slack, GitHub, Salesforce, or any of 500+ connectors once.
Scalekit stores and refreshes their credentials (OAuth 2.0, API keys, RSA key
pairs, and more) in an encrypted token vault, and returns 20,000+ tools as native
ADK tool objects that run with that user's own credentials. Tools can also be
served over MCP from Virtual MCP servers that expose only the tools a given agent
needs, and every tool call is logged for audit.

## Use cases

- **Personal assistants**: Build agents that read and send email, check
  calendars, and post to Slack as the signed-in user, with that user's own
  permissions.

- **Team agents with scoped tools**: Give a support agent only helpdesk and Slack
  tools, and a sales agent only CRM tools, by serving each from its own Virtual
  MCP server.

- **Engineering workflows**: Create agents that triage GitHub issues, open Linear
  or Jira tickets, and summarize pull requests on behalf of the engineer who asked.

- **Regulated environments**: Keep an audit trail of every tool call, stream it to
  your SIEM, and use Scalekit's SOC 2 Type II, HIPAA BAA, and VPC or self-hosted
  deployment options.

## Prerequisites

- A [Scalekit account](https://app.scalekit.com) with your environment URL,
  client ID, and client secret
- A connection for each app your agent uses, for example `gmail`
  ([set up a connection](https://docs.scalekit.com/agentkit/connections/))
- A [Gemini API key](https://aistudio.google.com/apikey)

## Installation

```bash
pip install scalekit-sdk-python google-adk
```

## Use with agent

!!! tip "Environment variables"

    Set your credentials as environment variables before running the examples below:

    ```bash
    export SCALEKIT_ENVIRONMENT_URL="https://your-env.scalekit.dev"
    export SCALEKIT_CLIENT_ID="your-client-id"
    export SCALEKIT_CLIENT_SECRET="your-client-secret"
    export GOOGLE_API_KEY="your-google-api-key"
    ```

Scalekit returns tools as native ADK tool objects, so you can pass them straight
to an `Agent`:

```python
import asyncio
import os

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from scalekit import ScalekitClient

scalekit = ScalekitClient(
    env_url=os.environ["SCALEKIT_ENVIRONMENT_URL"],
    client_id=os.environ["SCALEKIT_CLIENT_ID"],
    client_secret=os.environ["SCALEKIT_CLIENT_SECRET"],
)
actions = scalekit.actions

user_id = "user_123"  # your app's identifier for the end user
connection_name = "gmail"  # a connection configured in Scalekit

# The user authorizes the app once; send them the link if they haven't yet
account = actions.get_or_create_connected_account(
    connection_name=connection_name, identifier=user_id
).connected_account
if account.status != "ACTIVE":
    link = actions.get_authorization_link(
        connection_name=connection_name, identifier=user_id
    )
    raise SystemExit(f"Authorize Gmail first: {link.link}")

# Native ADK tools that run with this user's credentials
tools = actions.google.get_tools(
    identifier=user_id,
    connection_names=[connection_name],
    page_size=100,
)

agent = Agent(
    model="gemini-flash-latest",
    name="gmail_assistant",
    description="Reads and summarizes the user's Gmail through Scalekit.",
    instruction=(
        "You are a helpful email assistant. "
        "Use the available Gmail tools to answer the user's request."
    ),
    tools=tools,
)


async def main():
    async with InMemoryRunner(agent=agent) as runner:
        await runner.run_debug("Summarize my five most recent unread emails.")


asyncio.run(main())
```

### Connect over MCP

To give an agent tools from several connections behind one URL, or only the
tools its role needs, create a
[Virtual MCP server](https://docs.scalekit.com/agentkit/mcp/overview/) and
connect ADK's `McpToolset` with a session token minted for one user:

```python
from datetime import timedelta

from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

session = actions.mcp.create_session_token(
    mcp_config_id=os.environ["SCALEKIT_MCP_CONFIG_ID"],
    identifier=user_id,
    expiry=timedelta(hours=1),
)

agent = Agent(
    model="gemini-flash-latest",
    name="support_assistant",
    instruction="You are a support assistant. Use the available tools to help the user.",
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=os.environ["SCALEKIT_MCP_SERVER_URL"],
                headers={"Authorization": f"Bearer {session.token}"},
            )
        )
    ],
)
```

A session token is bound to one user and one server, lasts between 60 seconds
and 24 hours, and can be minted read-only (`access_level="READ_ONLY"`) so the
agent sees only tools that don't change anything.

## Available tools

Scalekit tools are discovered at runtime from the connections you configure, so
the tools available to your agent depend on which apps you connect. Browse the
[connector catalog](https://docs.scalekit.com/agentkit/connectors/) for the full
list, or print the tools for a connection:

```python
for tool in actions.google.get_tools(
    identifier=user_id, connection_names=["gmail"], page_size=100
):
    print(f"{tool.name}: {tool.description}")
```

## Resources

- [Scalekit Google ADK guide](https://docs.scalekit.com/agentkit/examples/google-adk/)
- [Scalekit documentation](https://docs.scalekit.com/agentkit/overview/)
- [Connector catalog](https://docs.scalekit.com/agentkit/connectors/)
- [Virtual MCP servers](https://docs.scalekit.com/agentkit/mcp/overview/)
- [Scalekit Python SDK](https://github.com/scalekit-inc/scalekit-sdk-python)
