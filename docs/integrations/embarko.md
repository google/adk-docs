---
catalog_title: Embarko
catalog_description: Deploy and host AI-built apps and websites, and get a live URL without any DevOps setup
catalog_icon: /integrations/assets/embarko.png
catalog_tags: ["deployment", "mcp"]
---

# Embarko MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Embarko](https://embarko.ai) is a deployment platform for AI-built apps and
websites. The [Embarko MCP server](https://github.com/walkover-mcp/embarko)
connects your ADK agent directly to Embarko, letting it deploy, update, and
manage live apps without any DevOps setup. Deployed apps are served at
`https://<app-name>.embarko.app`.

The server is hosted remotely at `https://mcp.embarko.ai/mcp` — nothing to
install locally.

## Use cases

- **Deploy apps from code**: An agent generates an app and immediately deploys
  it to a live URL, sharing it with users in the same conversation.
- **Iterate on live apps**: Update running apps, roll back to a previous
  version, or manage environment variables without leaving the agent session.
- **Monitor and debug**: Read logs, check deployment status, view analytics, and
  manage custom domains for any app the agent has deployed.

## Prerequisites

- An [Embarko](https://embarko.ai) account (free to sign up)
- An Embarko OAuth token — sign in at [embarko.ai](https://embarko.ai) and
  generate a token from your account settings, or authenticate through the MCP
  client's OAuth flow

## Use with agent

=== "Python"

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        EMBARKO_TOKEN = "YOUR_EMBARKO_TOKEN"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="deploy_agent",
            instruction="Help users deploy and manage their apps on Embarko",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mcp.embarko.ai/mcp",
                        headers={
                            "Authorization": f"Bearer {EMBARKO_TOKEN}",
                        },
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";
        import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";

        const EMBARKO_TOKEN = "YOUR_EMBARKO_TOKEN";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "deploy_agent",
            instruction: "Help users deploy and manage their apps on Embarko",
            tools: [
                new MCPToolset({
                    connectionParams: {
                        url: "https://mcp.embarko.ai/mcp",
                        headers: {
                            Authorization: `Bearer ${EMBARKO_TOKEN}`,
                        },
                    },
                }),
            ],
        });
        ```

## Available tools

Tool | Description
---- | -----------
`deploy_app` | Deploy or update an app from its source files (`appName`, `files`, optional `appType`, `version`)
`read_app` | Read app status, logs, deployments, environment variables, domains, and analytics
`update_app` | Set environment variables, register and verify a custom domain, roll back, or submit feedback
`app_danger_zone` | Delete an environment variable or domain, rename, or delete an app

## Resources

- [Embarko Quickstart](https://embarko.ai/docs/quickstart)
- [GitHub Repository](https://github.com/walkover-mcp/embarko)
- [MCP Registry listing](https://registry.mcp.so/server/io.github.swayammaheshwari/embarko-mcp)
