---
catalog_title: Browserbase
catalog_description: AI browser automation with Browserbase MCP and Stagehand
catalog_icon: /adk-docs/integrations/assets/browserbase.png
catalog_tags: ["mcp"]
---

# Browserbase MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Browserbase MCP Server](https://docs.browserbase.com/integrations/mcp/introduction) gives ADK agents
access to reliable browser automation powered by
[Stagehand](https://docs.stagehand.dev/v3/first-steps/introduction). With
these tools, agents can navigate websites, perform actions using natural
language, extract structured data, and capture screenshots.

![Browserbase MCP in action](/adk-docs/integrations/assets/browserbase-mcp.png)

## Use cases

- **Web navigation and automation**: Handle multi-step browser tasks such as
  login flows, form filling, and checkout sequences.
- **Structured extraction**: Pull product data, research data points, or other
  page content into machine-readable formats.
- **Agentic browsing workflows**: Combine navigation, actions, and extraction
  into robust end-to-end automations with ADK agents.

## Prerequisites

- Browserbase API key
- Browserbase project ID
- Google ADK installed
- Optional (local MCP mode only): Gemini API key for Stagehand model calls

## Installation

```bash
# Python ADK runtime
pip install google-adk

# TypeScript ADK runtime
npm install @google/adk
```

## Use with agent

=== "Python"

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="browserbase_agent",
            instruction="Help users automate websites and extract web information.",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPServerParams(
                        url="YOUR_SMITHERY_STREAMABLE_HTTP_URL",
                    ),
                )
            ],
        )
        ```

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        BROWSERBASE_API_KEY = "YOUR_BROWSERBASE_API_KEY"
        BROWSERBASE_PROJECT_ID = "YOUR_BROWSERBASE_PROJECT_ID"
        GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="browserbase_agent",
            instruction="Help users automate websites and extract web information.",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=["-y", "@browserbasehq/mcp-server-browserbase"],
                            env={
                                "BROWSERBASE_API_KEY": BROWSERBASE_API_KEY,
                                "BROWSERBASE_PROJECT_ID": BROWSERBASE_PROJECT_ID,
                                "GEMINI_API_KEY": GEMINI_API_KEY,
                            },
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "browserbase_agent",
            instruction: "Help users automate websites and extract web information.",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "YOUR_SMITHERY_STREAMABLE_HTTP_URL",
                }),
            ],
        });

        export { rootAgent };
        ```

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const BROWSERBASE_API_KEY = "YOUR_BROWSERBASE_API_KEY";
        const BROWSERBASE_PROJECT_ID = "YOUR_BROWSERBASE_PROJECT_ID";
        const GEMINI_API_KEY = "YOUR_GEMINI_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "browserbase_agent",
            instruction: "Help users automate websites and extract web information.",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "@browserbasehq/mcp-server-browserbase"],
                        env: {
                            BROWSERBASE_API_KEY: BROWSERBASE_API_KEY,
                            BROWSERBASE_PROJECT_ID: BROWSERBASE_PROJECT_ID,
                            GEMINI_API_KEY: GEMINI_API_KEY,
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## Available tools

Tool | Description
---- | -----------
`browserbase_stagehand_navigate` | Navigate to a URL
`browserbase_stagehand_act` | Perform actions via natural-language instructions
`browserbase_stagehand_extract` | Extract structured content from a page
`browserbase_stagehand_observe` | Identify actionable elements and page affordances
`browserbase_screenshot` | Capture screenshots during execution
`browserbase_stagehand_get_url` | Return the current page URL
`browserbase_session_create` | Create a browser session
`browserbase_session_close` | Close the current browser session

## Additional resources

- [Browserbase MCP docs](https://docs.browserbase.com/integrations/mcp/introduction)
- [Browserbase Google ADK setup docs](https://docs.browserbase.com/integrations/google-adk/setup)
- [Browserbase MCP server repository](https://github.com/browserbase/mcp-server-browserbase)
- [Stagehand documentation](https://docs.stagehand.dev/)
- [Browserbase](https://www.browserbase.com/)
