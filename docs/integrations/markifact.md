---
catalog_title: Markifact
catalog_description: Manage 300+ marketing operations across Google Ads, Meta Ads, GA4, TikTok Ads, LinkedIn Ads, Shopify, HubSpot, and 15+ more platforms
catalog_icon: /integrations/assets/markifact.png
catalog_tags: ["mcp", "connectors"]
---

# Markifact MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Markifact](https://www.markifact.com) is a remote MCP server that gives your
ADK agent a single, governed entry point into the full performance marketing
stack — paid media, analytics, e-commerce, CRM, and messaging — across 20+
platforms and 300+ operations. The [open-source MCP
server](https://github.com/markifact/markifact-mcp) handles OAuth, account
resolution, and write-time approval prompts, so your agent can plan and
execute end-to-end campaigns without you wiring up a separate API client per
platform.

## How it works

Rather than exposing all 300+ operations as tools (which blows up context and
degrades model accuracy), Markifact ships a small **meta-tool surface** that
your agent uses to look operations up at runtime:

- `find_operations` — semantic search over the operation registry, scoped by
  platform and intent. Returns a `requires_approval` flag that tells the agent
  whether to dispatch to the read or write path.
- `get_operation_inputs` — JSON Schema for a specific operation's inputs.
- `run_operation` / `run_write_operation` — execute reads and writes; writes
  follow a four-step approval protocol so spend never moves without explicit
  user confirmation.
- `list_connections`, `get_file_url`, `read_file`, `upload_media` —
  housekeeping for OAuth state and asset handoff.

A typical session looks like: the user describes an outcome ("audit last week's
Google Ads spend"), the agent searches the registry, inspects inputs, runs
reads, summarises, and only then proposes writes for approval. Connections
resolve automatically from the user's Markifact workspace; ad account selection
is always explicit.

## Use cases

- **Spend hygiene** — surface wasted budget across Google Ads, Meta, TikTok and
  LinkedIn with concrete pause and reallocation recommendations.
- **Unified reporting** — one prompt produces blended spend, ROAS, CAC and
  conversion deltas across every connected channel and GA4.
- **Briefs to live campaigns** — go from a one-line brief to drafted Search,
  Performance Max, Meta Advantage+, TikTok or LinkedIn campaigns ready for
  human approval.
- **Creative lifecycle** — detect fatigue, generate variants, and rotate
  creative on a schedule without leaving the agent.
- **Funnel analysis** — query GA4 paths, identify drop-off, and tie events back
  to the ad sets and keywords that drove them.
- **Commerce ↔ ads loop** — reconcile Shopify product performance against ad
  spend to find over- and under-invested SKUs.
- **Lead handoff** — sweep Meta and LinkedIn lead forms, enrich in HubSpot or
  Klaviyo, and trigger WhatsApp or Slack follow-ups.

## Prerequisites

- A [Markifact](https://www.markifact.com) account (free tier available).
- At least one platform connected from the Markifact dashboard (Google Ads,
  Meta, GA4, Shopify, etc.).
- See the [Markifact docs](https://www.markifact.com) for connection setup.

## Use with agent

=== "Python"

    === "Local MCP Server"

        When you run this agent for the first time, a browser window opens
        automatically to request access via OAuth. Approve the request in
        your browser to grant the agent access to your connected accounts.

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

    === "Remote MCP Server"

        If you already have a Markifact access token, you can connect directly
        using Streamable HTTP without the OAuth browser flow.

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

=== "TypeScript"

    === "Local MCP Server"

        When you run this agent for the first time, a browser window opens
        automatically to request access via OAuth. Approve the request in
        your browser to grant the agent access to your connected accounts.

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

    === "Remote MCP Server"

        If you already have a Markifact access token, you can connect directly
        using Streamable HTTP without the OAuth browser flow.

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

## Capabilities

Operations are discovered at runtime through the meta-tool surface, so adding
or updating platforms doesn't change your agent code or its context window.

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
- [MCP Registry Entry (`com.markifact/mcp`)](https://registry.modelcontextprotocol.io/v0.1/servers?search=com.markifact/mcp)
- [Skills on skills.sh](https://skills.sh/markifact/markifact-mcp)
