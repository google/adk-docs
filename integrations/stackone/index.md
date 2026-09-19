# StackOne plugin for ADK

Supported in ADKPython

The [StackOne ADK Plugin](https://github.com/StackOneHQ/stackone-adk-plugin) connects your ADK agent to hundreds of providers through [StackOne's](https://stackone.com) unified AI Integration gateway. Instead of manually defining tool functions for each API, this plugin dynamically discovers available tools from your connected providers and exposes them as native tools in ADK. It supports Human Resources Information Systems (HRIS), Applicant Tracking Systems (ATS), Customer Relationship Management (CRM), productivity and scheduling tools, and many more [integrations](https://www.stackone.com/connectors).

## Use cases

- **Sales and Revenue Operations**: Build agents that find leads in your CRM (e.g. HubSpot, Salesforce), enrich contact data, draft personalized outreach, and log activity back — all within one conversation.
- **People Operations**: Create agents that screen candidates in your ATS (e.g. Greenhouse, Ashby), check availability in your calendar tool (e.g. Google Calendar, Calendly), collect interview scorecards, move applicants through pipeline stages, and automate onboarding into your HRIS (e.g. BambooHR, Workday) — covering the full employee lifecycle without manual intervention.
- **Marketing Automation**: Build campaign agents that sync audience segments from your CRM to your email platform (e.g. Mailchimp, Klaviyo), trigger email sequences, and report on engagement metrics across channels.
- **Product Delivery**: Create agents that triage incoming feedback from your support tools (e.g. Intercom, Zendesk, Slack), prioritize and create issues in your project management tool (e.g. Linear, Jira), and resolve incidents using insights from an observability platform (e.g. PagerDuty, Datadog) — uniting product research, delivery, and reliability in a single workflow.

## Prerequisites

- A [StackOne account](https://app.stackone.com) with at least one connected provider
- A StackOne API key from the [StackOne Dashboard](https://app.stackone.com)
- A [Gemini API key](https://aistudio.google.com/apikey)

## Installation

```bash
pip install stackone-adk
```

Or with uv:

```bash
uv add stackone-adk
```

## Use with agent

Environment variables

Set your API keys as environment variables before running the examples below:

```bash
export STACKONE_API_KEY="your-stackone-api-key"
export GOOGLE_API_KEY="your-google-api-key"
```

Once `STACKONE_API_KEY` is set, the plugin automatically reads it and discovers your connected accounts.

```python
import asyncio

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from stackone_adk import StackOnePlugin


async def main():
    plugin = StackOnePlugin()
    # Or scope to a specific account:
    # plugin = StackOnePlugin(account_id="YOUR_ACCOUNT_ID")

    tools = plugin.get_tools()
    print(f"Discovered {len(tools)} tools")

    agent = Agent(
        model="gemini-flash-latest",
        name="scheduling_agent",
        description="Manages scheduling, HR, and CRM through StackOne.",
        instruction=(
            "You are a helpful assistant powered by StackOne. "
            "You help users manage their scheduling, HR, and CRM tasks "
            "by using the available tools.\n\n"
            "Always be helpful and provide clear, organized responses."
        ),
        tools=tools,
    )

    app = App(
        name="scheduling_app",
        root_agent=agent,
        plugins=[plugin],
    )

    async with InMemoryRunner(app=app) as runner:
        events = await runner.run_debug(
            "Get my most recent scheduled meeting from Calendly.",
            quiet=True,
        )
        # Extract the agent's final text response
        for event in reversed(events):
            if event.content and event.content.parts:
                text_parts = [p.text for p in event.content.parts if p.text]
                if text_parts:
                    print("".join(text_parts))
                    break


asyncio.run(main())
```

```python
import asyncio

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from stackone_adk import StackOnePlugin


async def main():
    plugin = StackOnePlugin()
    # Or scope to a specific account:
    # plugin = StackOnePlugin(account_id="YOUR_ACCOUNT_ID")

    tools = plugin.get_tools()
    print(f"Discovered {len(tools)} tools")

    agent = Agent(
        model="gemini-flash-latest",
        name="scheduling_agent",
        description="Manages scheduling, HR, and CRM through StackOne.",
        instruction=(
            "You are a helpful assistant powered by StackOne. "
            "You help users manage their scheduling, HR, and CRM tasks "
            "by using the available tools.\n\n"
            "Always be helpful and provide clear, organized responses."
        ),
        tools=tools,
    )

    async with InMemoryRunner(
        app_name="scheduling_app", agent=agent
    ) as runner:
        events = await runner.run_debug(
            "Get my most recent scheduled meeting from Calendly.",
            quiet=True,
        )
        # Extract the agent's final text response
        for event in reversed(events):
            if event.content and event.content.parts:
                text_parts = [p.text for p in event.content.parts if p.text]
                if text_parts:
                    print("".join(text_parts))
                    break


asyncio.run(main())
```

## Search and execute mode

With `mode="search_and_execute"`, the plugin registers exactly two tools, `tool_search` and `tool_execute`. The model uses them at runtime to discover the right StackOne tool and invoke it, instead of seeing the full catalog upfront.

Registering every tool definition with the model has three costs:

- **Token overhead:** Tool schemas consume prompt tokens that could otherwise be available for reasoning.
- **Payload limits:** Large catalogs can exceed provider payload limits. Gemini, for example, imposes hard limits on the size and number of function declarations per request.
- **Selection accuracy:** Tool-selection quality degrades as the tool candidate set grows, since the model has more near-duplicates to disambiguate.

This mode keeps the registered tool count at two regardless of catalog size. The model resolves the right tool through a natural-language query at runtime.

This mode requires `stackone-adk>=0.2.0`.

```python
import asyncio

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from stackone_adk import StackOnePlugin


async def main():
    plugin = StackOnePlugin(
        mode="search_and_execute",
        account_ids=["YOUR_ACCOUNT_ID"],
        search={"method": "auto", "top_k": 10},
    )

    agent = Agent(
        model="gemini-flash-latest",
        name="stackone_agent",
        description="Connects to multiple SaaS providers through StackOne.",
        instruction=(
            "You are an assistant powered by StackOne. To answer the "
            "user's request, first call tool_search with a short query "
            "to find the right action, then call tool_execute with the "
            "chosen tool name and parameters that match the schema "
            "returned by tool_search."
        ),
        tools=plugin.get_tools(),
    )

    app = App(
        name="stackone_app",
        root_agent=agent,
        plugins=[plugin],
    )

    async with InMemoryRunner(app=app) as runner:
        events = await runner.run_debug(
            "List the first 3 workers.",
            quiet=True,
        )
        for event in reversed(events):
            if event.content and event.content.parts:
                text_parts = [p.text for p in event.content.parts if p.text]
                if text_parts:
                    print("".join(text_parts))
                    break


asyncio.run(main())
```

The model first calls `tool_search` with a natural-language query and receives a short list of candidate tools, each with its name, description, and parameter schema. The model then calls `tool_execute` with the selected tool name and parameters that match the schema. Both calls route through StackOne's AI Integration Gateway via the SDK.

## Available tools

Unlike integrations with a fixed set of tools, StackOne tools are **dynamically discovered** from your connected providers via the StackOne API. The available tools depend on which SaaS providers you have connected in your [StackOne Dashboard](https://app.stackone.com).

To list discovered tools:

```python
plugin = StackOnePlugin(account_id="YOUR_ACCOUNT_ID") # Optional: omit to use all connected accounts
for tool in plugin.get_tools():
    print(f"{tool.name}: {tool.description}")
```

### Supported integration categories

| Category            | Example providers                                               |
| ------------------- | --------------------------------------------------------------- |
| HRIS                | HiBob, BambooHR, Workday, SAP SuccessFactors, Personio, Gusto   |
| ATS                 | Greenhouse, Ashby, Lever, Bullhorn, SmartRecruiters, Teamtailor |
| CRM & Sales         | Salesforce, HubSpot, Pipedrive, Zoho CRM, Close, Copper         |
| Marketing           | Mailchimp, Klaviyo, ActiveCampaign, Brevo, GetResponse          |
| Ticketing & Support | Zendesk, Freshdesk, Jira, ServiceNow, PagerDuty, Linear         |
| Productivity        | Asana, ClickUp, Slack, Microsoft Teams, Notion, Confluence      |
| Scheduling          | Calendly, Cal.com                                               |
| LMS & Learning      | 360Learning, Docebo, Go1, Cornerstone, LinkedIn Learning        |
| Commerce            | Shopify, BigCommerce, WooCommerce, Etsy                         |
| Developer Tools     | GitHub, GitLab, Twilio                                          |

For a complete list of 200+ supported providers, visit the [StackOne integrations page](https://www.stackone.com/connectors).

## Configuration

### Plugin parameters

| Parameter     | Type                            | Default             | Description                                                                                                         |
| ------------- | ------------------------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `api_key`     | \`str                           | None\`              | `None`                                                                                                              |
| `account_id`  | \`str                           | None\`              | `None`                                                                                                              |
| `base_url`    | \`str                           | None\`              | `None`                                                                                                              |
| `plugin_name` | `str`                           | `"stackone_plugin"` | Plugin identifier for ADK.                                                                                          |
| `providers`   | \`list[str]                     | None\`              | `None`                                                                                                              |
| `actions`     | \`list[str]                     | None\`              | `None`                                                                                                              |
| `account_ids` | \`list[str]                     | None\`              | `None`                                                                                                              |
| `mode`        | \`Literal["search_and_execute"] | None\`              | `None`                                                                                                              |
| `search`      | \`SearchConfig                  | None\`              | `None`                                                                                                              |
| `execute`     | \`ExecuteToolsConfig            | None\`              | `None`                                                                                                              |
| `timeout`     | `float`                         | `180.0`             | Per-request timeout in seconds for HTTP calls (account discovery and tool execution). Increase for slow connectors. |

### Tool filtering

Filter tools by provider, action pattern, account ID, or any combination:

```python
# Specify accounts
plugin = StackOnePlugin(account_ids=["acct-hibob-1", "acct-bamboohr-1"])

# Read-only operations
plugin = StackOnePlugin(actions=["*_list_*", "*_get_*"])

# Specific actions with glob patterns
plugin = StackOnePlugin(actions=["calendly_list_events", "calendly_get_event_*"])

# Combined filters
plugin = StackOnePlugin(
    actions=["*_list_*", "*_get_*"],
    account_ids=["acct-hibob-1"],
)
```

## Additional resources

- [StackOne ADK Plugin Repository](https://github.com/StackOneHQ/stackone-adk-plugin)
- [StackOne Documentation](https://docs.stackone.com/)
- [StackOne Dashboard](https://app.stackone.com)
- [StackOne Python AI SDK](https://github.com/StackOneHQ/stackone-ai-python)
