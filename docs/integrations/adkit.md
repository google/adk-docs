---
catalog_title: AdKit
catalog_description: Manage ad campaigns and read their results on Meta, Google, TikTok, and five more platforms
catalog_icon: /integrations/assets/adkit.png
catalog_tags: ["mcp", "connectors"]
---

# AdKit MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [AdKit MCP Server](https://github.com/adkit/ads-mcp) connects your ADK agent
to [AdKit](https://adkit.so/features/ads-mcp). AdKit is a hosted service that
manages ads on Meta, Google, TikTok, LinkedIn, Microsoft, Reddit, X, and
Pinterest. Your agent can read campaign results, create and edit campaigns, and
browse competitor ads. By default, AdKit saves each change as a draft. The agent
publishes a draft only after you approve it.

## Use cases

- **Performance reporting**: read spend, impressions, clicks, conversions, and
  ROAS for the ad accounts in a project. On Google Ads, the agent can also read
  search terms and placements.
- **Campaign drafts**: create or edit campaigns, ad sets, and ads from a prompt.
  Each change stays a draft until you review and approve it.
- **Competitor research**: search the AdKit ad library for ads that other
  advertisers run on Meta, Google, and LinkedIn. The agent can also keep a
  watchlist of advertisers and save ads to boards.
- **Ad creatives**: generate static ad images from a brief. The agent can also
  upload image and video files to an ad account.
- **Website data**: read GA4 reports, and Google Search Console keywords and
  pages. This data is in the same project as your ad accounts.

## Prerequisites

- An AdKit account. A free account includes 50 actions. Paid plans start at
  $29 per month, with a 7-day free trial. See
  [pricing](https://adkit.so/pricing).
- At least one ad account connected to an AdKit project. See
  [Connect your ad accounts](https://adkit.so/docs/platforms).
- For Python: ADK installed with the MCP extra
  (`pip install "google-adk[mcp]"`).
- For the local example: Node.js, to run `npx mcp-remote`.
- For the remote example: an AdKit API key. In the AdKit dashboard, open
  **Connect Your Agent**, select **Other agent**, select
  **API key / Custom headers**, then select **Create API key**.

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
            name="adkit_agent",
            instruction=(
                "You help users report on and manage their ad campaigns with "
                "AdKit. Start with adkit_projects to pick a project. Save "
                "changes as drafts, and publish only after the user approves."
            ),
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "mcp-remote",
                                "https://mcp.adkit.so",
                            ],
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

        !!! note

            The first time you run this agent, a browser window opens for OAuth
            sign-in. Sign in with your AdKit account and approve the request.

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

        ADKIT_API_KEY = "YOUR_ADKIT_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="adkit_agent",
            instruction=(
                "You help users report on and manage their ad campaigns with "
                "AdKit. Start with adkit_projects to pick a project. Save "
                "changes as drafts, and publish only after the user approves."
            ),
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mcp.adkit.so",
                        headers={
                            "Authorization": f"Bearer {ADKIT_API_KEY}",
                        },
                    ),
                )
            ],
        )
        ```

        !!! note

            This example sends your AdKit API key as a Bearer token. It does
            not open a browser window for OAuth sign-in.

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "adkit_agent",
            instruction:
                "You help users report on and manage their ad campaigns with " +
                "AdKit. Start with adkit_projects to pick a project. Save " +
                "changes as drafts, and publish only after the user approves.",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: [
                            "-y",
                            "mcp-remote",
                            "https://mcp.adkit.so",
                        ],
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

        !!! note

            The first time you run this agent, a browser window opens for OAuth
            sign-in. Sign in with your AdKit account and approve the request.

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const ADKIT_API_KEY = "YOUR_ADKIT_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "adkit_agent",
            instruction:
                "You help users report on and manage their ad campaigns with " +
                "AdKit. Start with adkit_projects to pick a project. Save " +
                "changes as drafts, and publish only after the user approves.",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.adkit.so",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${ADKIT_API_KEY}`,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

        !!! note

            This example sends your AdKit API key as a Bearer token. It does
            not open a browser window for OAuth sign-in.

## Available tools

Tool | Description
---- | -----------
`adkit_projects` | List, create, or update AdKit projects
`adkit_status` | Show the platforms and ad accounts connected to a project
`adkit_setup` | Get the link that the user opens to connect an ad platform
`adkit_manage` | Read results, and create, edit, or publish campaigns, ad sets, and ads
`adkit_upload_file` | Upload one image or video file to an ad platform
`adkit_library` | Browse ads from other advertisers, manage a watchlist, and save ads to boards
`adkit_studio` | Create ad briefs and generate static ad images
`adkit_integrations` | Read GA4 reports and Google Search Console data
`adkit_help` | Look up field names, accepted values, and limits for each platform

## Supported platforms

Category | Platforms
-------- | ---------
Campaign management and reporting | Meta (Facebook and Instagram), Google Ads, TikTok, LinkedIn, Reddit, X
Direct platform API requests (beta) | Microsoft, Pinterest
Analytics (read-only) | GA4, Google Search Console
Ad library | Meta, Google, LinkedIn

Each platform supports different resources and fields. The `adkit_help` tool
lists them for each platform.

## Additional resources

- [AdKit Website](https://adkit.so/features/ads-mcp)
- [AdKit Documentation](https://adkit.so/docs/getting-started)
- [AdKit MCP Server on GitHub](https://github.com/adkit/ads-mcp)
