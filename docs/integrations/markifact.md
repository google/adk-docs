---
catalog_title: Markifact
catalog_description: Manage marketing operations across Google Ads, Meta, GA4, TikTok, and 15+ more platforms
catalog_icon: /integrations/assets/markifact.png
catalog_tags: ["mcp", "connectors"]
---

# Markifact MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Markifact MCP Server](https://github.com/markifact/markifact-mcp) connects
your ADK agent to [Markifact](https://www.markifact.com), an AI marketing
automation platform with 300+ operations across 20+ platforms including Google
Ads, Meta Ads, GA4, TikTok Ads, and Shopify. This integration gives your agent
the ability to manage campaigns, analyze performance, and automate marketing
workflows using natural language, with approval prompts on every write operation.

## Use cases

- **Spend hygiene**: surface wasted budget across Google Ads, Meta, TikTok and
  LinkedIn with concrete pause and reallocation recommendations.
- **Unified reporting**: one prompt produces blended spend, ROAS, CAC and
  conversion deltas across every connected channel and GA4.
- **Briefs to live campaigns**: go from a one-line brief to drafted Search,
  Performance Max, Meta Advantage+, TikTok or LinkedIn campaigns ready for
  human approval.
- **Lead handoff**: sweep Meta and LinkedIn lead forms, enrich in HubSpot or
  Klaviyo, and trigger WhatsApp or Slack follow-ups.

## Prerequisites

- A [Markifact](https://www.markifact.com) account (free tier available)
- At least one platform connected from the Markifact dashboard (Google Ads,
  Meta, GA4, Shopify, etc.)
- See the [Markifact docs](https://docs.markifact.com) for connection setup

## Use with agent

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        root_agent = Agent(
            model="gemini-flash-latest",
            name="marketing_agent",
            instruction=(
                "You are a performance marketing agent that helps users manage "
                "ad campaigns, run analytics, sync e-commerce data, and "
                "execute marketing workflows across Google Ads, Meta Ads, GA4, "
                "TikTok Ads, LinkedIn Ads, Shopify, HubSpot, and more. "
                "Always confirm with the user before any write operation."
            ),
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "mcp-remote",
                                "https://api.markifact.com/mcp",
                            ],
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

        !!! note

            When you run this agent for the first time, a browser window opens
            automatically to request access via OAuth. Approve the request in
            your browser to grant the agent access to your connected accounts.

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

        MARKIFACT_ACCESS_TOKEN = "YOUR_MARKIFACT_ACCESS_TOKEN"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="marketing_agent",
            instruction=(
                "You are a performance marketing agent that helps users manage "
                "ad campaigns, run analytics, sync e-commerce data, and "
                "execute marketing workflows across Google Ads, Meta Ads, GA4, "
                "TikTok Ads, LinkedIn Ads, Shopify, HubSpot, and more. "
                "Always confirm with the user before any write operation."
            ),
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://api.markifact.com/mcp",
                        headers={
                            "Authorization": f"Bearer {MARKIFACT_ACCESS_TOKEN}",
                        },
                    ),
                )
            ],
        )
        ```

        !!! note

            If you already have a Markifact access token, you can connect
            directly using Streamable HTTP without the OAuth browser flow.

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "marketing_agent",
            instruction:
                "You are a performance marketing agent that helps users manage " +
                "ad campaigns, run analytics, sync e-commerce data, and " +
                "execute marketing workflows across Google Ads, Meta Ads, GA4, " +
                "TikTok Ads, LinkedIn Ads, Shopify, HubSpot, and more. " +
                "Always confirm with the user before any write operation.",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: [
                            "-y",
                            "mcp-remote",
                            "https://api.markifact.com/mcp",
                        ],
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

        !!! note

            When you run this agent for the first time, a browser window opens
            automatically to request access via OAuth. Approve the request in
            your browser to grant the agent access to your connected accounts.

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const MARKIFACT_ACCESS_TOKEN = "YOUR_MARKIFACT_ACCESS_TOKEN";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "marketing_agent",
            instruction:
                "You are a performance marketing agent that helps users manage " +
                "ad campaigns, run analytics, sync e-commerce data, and " +
                "execute marketing workflows across Google Ads, Meta Ads, GA4, " +
                "TikTok Ads, LinkedIn Ads, Shopify, HubSpot, and more. " +
                "Always confirm with the user before any write operation.",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://api.markifact.com/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${MARKIFACT_ACCESS_TOKEN}`,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

        !!! note

            If you already have a Markifact access token, you can connect
            directly using Streamable HTTP without the OAuth browser flow.

## Available tools

Tool | Description
---- | -----------
`find_operations` | Semantic search over the operation registry, scoped by platform and intent
`get_operation_inputs` | Returns JSON Schema for a specific operation's inputs
`run_operation` | Execute read operations
`run_write_operation` | Execute write operations with approval protocol
`list_connections` | List OAuth connections in the workspace
`get_file_url` | Get URLs for reports and exports
`read_file` | Read file contents
`upload_media` | Upload media assets

## Capabilities

Capability | Description
---------- | -----------
Discovery | Semantic search over 300+ operations with read/write classification
Approval-gated writes | Four-step protocol around `run_write_operation` for any spend or destructive change
Campaign management | Create, edit, pause and resume campaigns, ad sets and ads across all paid channels
Reporting & attribution | Cross-platform spend, ROAS and conversion blends, plus GA4 path and channel analysis
Audiences | Custom audiences, lookalikes, exclusions and behavioural targeting per platform
Creative | Asset upload, variant rotation, fatigue detection and approval-gated publishing
Commerce & CRM | Shopify, HubSpot and Klaviyo sync with paid media for closed-loop reporting
Messaging | WhatsApp and Slack notifications for approvals, alerts and lead handoff
File I/O | Reports, exports and uploads via `get_file_url`, `read_file`, `upload_media`

## Supported platforms

Category | Platforms
-------- | ---------
Paid media | Google Ads, Meta Ads, TikTok Ads, LinkedIn Ads, Microsoft Ads, Reddit Ads, Pinterest Ads, Snapchat Ads, Amazon Ads, DV360
Analytics | GA4, BigQuery, Google Search Console, Google Merchant Center
E-commerce, CRM, messaging | Shopify, HubSpot, Klaviyo, WhatsApp, Slack
Organic & social | Facebook, Instagram, LinkedIn, Google Business Profile

## Additional resources

- [Markifact Website](https://www.markifact.com)
- [Markifact MCP Server on GitHub](https://github.com/markifact/markifact-mcp)
- [Skills on skills.sh](https://skills.sh/markifact/markifact-mcp)
