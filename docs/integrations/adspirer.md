---
catalog_title: Adspirer
catalog_description: Create, manage, and optimize ad campaigns across Google, Meta, LinkedIn, and TikTok Ads
catalog_icon: /integrations/assets/adspirer.png
catalog_tags: ["mcp", "connectors"]
---

# Adspirer MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Adspirer MCP Server](https://github.com/amekala/ads-mcp) connects your ADK agent to
[Adspirer](https://www.adspirer.com/), an AI-powered advertising platform with
100+ tools across Google Ads, Meta Ads, LinkedIn Ads, and TikTok Ads. This
integration gives your agent the ability to create, manage, and optimize ad
campaigns using natural language — from keyword research and audience planning to
campaign launch and performance analysis.

## How it works

Adspirer is a remote MCP server that acts as a bridge between your ADK agent and
advertising platforms. Your agent connects to Adspirer's MCP endpoint, authenticates
via OAuth 2.1, and gains access to 100+ tools that map directly to ad platform APIs.

The typical workflow looks like this:

1. **Connect** — Your ADK agent connects to `https://mcp.adspirer.com/mcp` and
   authenticates via OAuth 2.1. On first run, a browser window opens for you to
   sign in and authorize access to your ad accounts.
2. **Discover** — The agent discovers available tools based on your connected ad
   platforms (Google Ads, Meta Ads, LinkedIn Ads, TikTok Ads).
3. **Execute** — The agent can now execute the full campaign lifecycle through
   natural language: research keywords, plan audiences, create campaigns, analyze
   performance, optimize budgets, and manage ads — all without touching a dashboard.

Adspirer handles OAuth token management, ad platform API calls, and safety
guardrails (e.g., cannot delete campaigns or modify existing budgets) so your
agent can operate autonomously with built-in protections.

## Use cases

- **Campaign Creation**: Launch complex ad campaigns across Google, Meta,
  LinkedIn, and TikTok through natural language. Create Search, Performance Max,
  YouTube, Demand Gen, image, video, and carousel campaigns without touching a
  dashboard.

- **Performance Analysis**: Analyze campaign metrics across all connected ad
  platforms. Ask questions like "Which campaigns have the best ROAS?" or
  "Where am I wasting spend?" and get actionable insights with optimization
  recommendations.

- **Keyword Research & Planning**: Research keywords using Google Keyword Planner
  with real CPC data, search volumes, and competition analysis. Build keyword
  strategies and add them directly to campaigns.

- **Budget Optimization**: Identify underperforming campaigns, detect budget
  inefficiencies, and get AI-driven recommendations for spend allocation across
  channels and campaigns.

- **Ad Management**: Add new ad groups, ad sets, and ads to existing campaigns.
  A/B test creatives, update ad copy, manage keywords, and pause or resume
  campaigns — all through your agent.

## Prerequisites

- An [Adspirer](https://www.adspirer.com/) account (free tier available)
- At least one connected ad platform (Google Ads, Meta Ads, LinkedIn Ads, or
  TikTok Ads) — connect via your Adspirer dashboard after signing up
- See the [Quickstart guide](https://www.adspirer.com/docs/quickstart) for
  step-by-step setup instructions

## Use with agent

=== "Python"

    === "Local MCP Server"

        When you run this agent for the first time, a browser window opens
        automatically to request access via OAuth. Approve the request in
        your browser to grant the agent access to your connected ad accounts.

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        root_agent = Agent(
            model="gemini-flash-latest",
            name="advertising_agent",
            instruction=(
                "You are an advertising agent that helps users create, manage, "
                "and optimize ad campaigns across Google Ads, Meta Ads, "
                "LinkedIn Ads, and TikTok Ads."
            ),
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "mcp-remote",
                                "https://mcp.adspirer.com/mcp",
                            ],
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

    === "Remote MCP Server"

        If you already have an Adspirer access token, you can connect directly
        using Streamable HTTP without the OAuth browser flow.

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

        ADSPIRER_ACCESS_TOKEN = "YOUR_ADSPIRER_ACCESS_TOKEN"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="advertising_agent",
            instruction=(
                "You are an advertising agent that helps users create, manage, "
                "and optimize ad campaigns across Google Ads, Meta Ads, "
                "LinkedIn Ads, and TikTok Ads."
            ),
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mcp.adspirer.com/mcp",
                        headers={
                            "Authorization": f"Bearer {ADSPIRER_ACCESS_TOKEN}",
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
        your browser to grant the agent access to your connected ad accounts.

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "advertising_agent",
            instruction:
                "You are an advertising agent that helps users create, manage, " +
                "and optimize ad campaigns across Google Ads, Meta Ads, " +
                "LinkedIn Ads, and TikTok Ads.",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: [
                            "-y",
                            "mcp-remote",
                            "https://mcp.adspirer.com/mcp",
                        ],
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

    === "Remote MCP Server"

        If you already have an Adspirer access token, you can connect directly
        using Streamable HTTP without the OAuth browser flow.

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const ADSPIRER_ACCESS_TOKEN = "YOUR_ADSPIRER_ACCESS_TOKEN";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "advertising_agent",
            instruction:
                "You are an advertising agent that helps users create, manage, " +
                "and optimize ad campaigns across Google Ads, Meta Ads, " +
                "LinkedIn Ads, and TikTok Ads.",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.adspirer.com/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${ADSPIRER_ACCESS_TOKEN}`,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## Capabilities

Adspirer provides 100+ MCP tools for full-lifecycle ad campaign management
across four major advertising platforms.

Capability | Description
---------- | -----------
Campaign creation | Launch Search, PMax, YouTube, Demand Gen, image, video, and carousel campaigns
Performance analysis | Analyze metrics, detect anomalies, and get optimization recommendations
Keyword research | Research keywords with real CPC, search volume, and competition data
Budget optimization | AI-driven budget allocation and wasted spend detection
Ad management | Create and update ads, ad groups, ad sets, headlines, and descriptions
Audience targeting | Search interests, behaviors, job titles, and custom audiences
Asset management | Validate, upload, and discover existing creative assets
Campaign controls | Pause, resume, update bids, budgets, and targeting settings

## Supported platforms

Platform | Tools | Capabilities
-------- | ----- | ------------
Google Ads | 49 | Search, PMax, YouTube, Demand Gen campaigns, keyword research, ad extensions, audience signals
Meta Ads | 30+ | Image, video, carousel, DCO campaigns, pixel tracking, lead forms, audience insights
LinkedIn Ads | 28 | Sponsored content, lead gen, conversation ads, demographic targeting, engagement analysis
TikTok Ads | 4 | Campaign management and performance analysis

## Additional resources

- [Adspirer Website](https://www.adspirer.com/)
- [Adspirer MCP Server on GitHub](https://github.com/amekala/ads-mcp)
- [Quickstart Guide](https://www.adspirer.com/docs/quickstart)
- [Tool Catalog](https://www.adspirer.com/docs/agent-skills/tools)
- [Core Workflows](https://www.adspirer.com/docs/agent-skills/workflows)
- [Ad Platform Guides](https://www.adspirer.com/docs)
