---
catalog_title: StackOne Agent Connectors
catalog_description: Connect agents to 200+ SaaS providers
catalog_icon: /adk-docs/integrations/assets/stackone.png
catalog_tags: ["connectors"]
---

# StackOne plugin for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [StackOne ADK Plugin](https://github.com/StackOneHQ/stackone-adk-plugin)
connects your ADK agent to over 200 SaaS providers through
[StackOne's](https://stackone.com) unified API gateway. Instead of manually
defining tool functions for each API, this plugin dynamically discovers available
tools from your connected providers and exposes them as native Google ADK tools.
It supports HRIS, ATS, CRM, scheduling, and many more integration categories.

## Use cases

- **Sales and Revenue Operations**: Build agents that look up leads in HubSpot
  or Salesforce, enrich contact data, draft personalized outreach, and
  automatically log activities back to your CRM -- all in one conversation.

- **Recruiting and Talent Acquisition**: Create hiring agents that screen
  candidates in Greenhouse or Ashby, schedule interviews via Calendly, collect
  scorecards, and move applicants through pipeline stages without manual
  intervention.

- **HR and People Operations**: Automate employee onboarding workflows that
  provision accounts, assign training courses in your LMS, update records in
  BambooHR or Workday, and answer policy questions using data from your HRIS.

- **Marketing Automation**: Build campaign agents that sync audience segments
  from your CRM to Mailchimp or Klaviyo, trigger email sequences, and report
  on engagement metrics across channels.

- **Product Management**: Create agents that triage incoming feature requests
  from Intercom or Zendesk, create and prioritize issues in Linear or Jira,
  and surface relevant customer feedback from your support tools.

- **Engineering and SRE**: Build on-call agents that pull incident data from
  PagerDuty, create postmortem tickets in Jira, notify teams via Slack, and
  cross-reference deployment logs from GitHub -- bridging operational tools in
  a single agentic workflow.

- **Cross-Functional Workflows**: Combine data and actions across multiple SaaS
  providers in a single agent. For example, an agent that detects a closed-won
  deal in Salesforce, triggers onboarding tasks in Asana, provisions the
  customer in your billing system, and sends a welcome sequence via your
  marketing platform.

## Prerequisites

- A [StackOne account](https://app.stackone.com) with at least one connected
  provider
- A StackOne API key from the
  [StackOne Dashboard](https://app.stackone.com)
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

!!! tip "Environment variables"

    Set your API keys as environment variables before running the examples below:

    ```bash
    export STACKONE_API_KEY="your-stackone-api-key"
    export GOOGLE_API_KEY="your-google-api-key"
    ```

    Once `STACKONE_API_KEY` is set, the plugin automatically reads it and
    discovers your connected accounts — no constructor arguments needed.

=== "Python"

    === "With App (Recommended)"

        ```python
        import asyncio

        from google.adk.agents import Agent
        from google.adk.apps import App
        from google.adk.runners import InMemoryRunner
        from stackone_adk import StackOnePlugin

        async def main():
            plugin = StackOnePlugin(account_id="YOUR_ACCOUNT_ID")

            agent = Agent(
                model="gemini-2.5-flash",
                name="scheduling_agent",
                instruction="You are a scheduling assistant with access to Calendly.",
                tools=plugin.get_tools(),
            )

            app = App(
                name="scheduling_app",
                root_agent=agent,
                plugins=[plugin],
            )

            async with InMemoryRunner(app=app) as runner:
                response = await runner.run_debug("What event types do I have?")
                print(response)

        asyncio.run(main())
        ```

    === "With Runner Directly"

        ```python
        import asyncio

        from google.adk.agents import Agent
        from google.adk.runners import InMemoryRunner
        from stackone_adk import StackOnePlugin

        async def main():
            plugin = StackOnePlugin(account_id="YOUR_ACCOUNT_ID")

            agent = Agent(
                model="gemini-2.5-flash",
                name="scheduling_agent",
                instruction="You are a scheduling assistant with access to Calendly.",
                tools=plugin.get_tools(),
            )

            async with InMemoryRunner(
                app_name="scheduling_app", agent=agent
            ) as runner:
                response = await runner.run_debug("List my events")
                print(response)

        asyncio.run(main())
        ```

## Available tools

Unlike integrations with a fixed set of tools, StackOne tools are **dynamically
discovered** from your connected providers via the StackOne API. The available
tools depend on which SaaS providers you have connected in your
[StackOne Dashboard](https://app.stackone.com).

To list discovered tools:

```python
plugin = StackOnePlugin(account_id="YOUR_ACCOUNT_ID")
for tool in plugin.get_tools():
    print(f"{tool.name}: {tool.description}")
```

### Supported integration categories

Category | Example providers
-------- | -----------------
HRIS | HiBob, BambooHR, Workday, SAP SuccessFactors, Personio, Gusto
ATS | Greenhouse, Ashby, Lever, Bullhorn, SmartRecruiters, Teamtailor
CRM & Sales | Salesforce, HubSpot, Pipedrive, Zoho CRM, Close, Copper
Marketing | Mailchimp, Klaviyo, ActiveCampaign, Brevo, GetResponse
Ticketing & Support | Zendesk, Freshdesk, Jira, ServiceNow, PagerDuty, Linear
Productivity | Asana, ClickUp, Slack, Microsoft Teams, Notion, Confluence
Scheduling | Calendly, Cal.com
LMS & Learning | 360Learning, Docebo, Go1, Cornerstone, LinkedIn Learning
Commerce | Shopify, BigCommerce, WooCommerce, Etsy
Developer Tools | GitHub, GitLab, Twilio

For a complete list of 200+ supported providers, visit the
[StackOne integrations page](https://www.stackone.com/integrations).

## Configuration

### Plugin parameters

Parameter | Type | Default | Description
--------- | ---- | ------- | -----------
`api_key` | `str \| None` | `None` | StackOne API key. Falls back to `STACKONE_API_KEY` env var.
`account_id` | `str \| None` | `None` | Default account ID for all tools.
`base_url` | `str \| None` | `None` | API URL override (default: `https://api.stackone.com`).
`plugin_name` | `str` | `"stackone_plugin"` | Plugin identifier for ADK.
`providers` | `list[str] \| None` | `None` | Filter by provider names (e.g., `["calendly", "hibob"]`).
`actions` | `list[str] \| None` | `None` | Filter by action patterns using glob syntax.
`account_ids` | `list[str] \| None` | `None` | Scope tools to specific connected account IDs.

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
