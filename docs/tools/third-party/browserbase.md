# Browserbase

The
[Browserbase MCP Server](https://github.com/browserbase/mcp-server-browserbase)
connects to cloud browser automation capabilities using
[Browserbase](https://www.browserbase.com/) and
[Stagehand](https://github.com/browserbase/stagehand). It enables your ADK agent
to interact with web pages, take screenshots, extract information, and perform
automated actions.

## Use cases

- **Automated Web Workflows**: Empower your agent to perform multi-step tasks
  like logging into websites, filling out forms, submitting data, and navigating
  complex user flows.

- **Intelligent Data Extraction**: Automatically browse to specific pages and
extract structured data, text content, or other information for use in your
agent's tasks.

- **Visual Monitoring & Interaction**: Capture full-page or element-specific
screenshots to visually monitor websites, test UI elements, or feed visual
context back to a vision-enabled model.

## Prerequisites

- Sign up for a [Browserbase account](https://www.browserbase.com/sign-up) to
  obtain an API key and project ID. Refer to the
  [documentation](https://docs.browserbase.com/introduction/getting-started) for
  more information.

## Use with agent

=== "Local MCP Server"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
    from mcp import StdioServerParameters

    BROWSERBASE_API_KEY = "YOUR_BROWSERBASE_API_KEY"
    BROWSERBASE_PROJECT_ID = "YOUR_BROWSERBASE_PROJECT_ID"
    GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="browserbase_agent",
        instruction="Help users get information from Browserbase",
        tools=[
            MCPToolset(
                connection_params=StdioConnectionParams(
                    server_params = StdioServerParameters(
                        command="npx",
                        args=[
                            "-y",
                            "@browserbasehq/mcp-server-browserbase",
                        ],
                        env={
                            "BROWSERBASE_API_KEY": BROWSERBASE_API_KEY,
                            "BROWSERBASE_PROJECT_ID": BROWSERBASE_PROJECT_ID,
                            "GEMINI_API_KEY": GEMINI_API_KEY,
                        }
                    ),
                    timeout=300,
                ),
            )
        ],
    )
    ```

## Available tools

Tool <img width="200px"/> | Description
---- | -----------
`browserbase_stagehand_navigate` | Navigate to any URL in the browser
`browserbase_stagehand_act` | Perform an action on the web page using natural language
`browserbase_stagehand_extract` | Extract all text content from the current page (filters out CSS and JavaScript)
`browserbase_stagehand_observe` | Observe and find actionable elements on the web page
`browserbase_screenshot` | Capture a PNG screenshot of the current page
`browserbase_stagehand_get_url` | Get the current URL of the browser page
`browserbase_session_create` | Create or reuse a cloud browser session using Browserbase with fully initialized Stagehand
`browserbase_session_close` | Close the current Browserbase session, disconnect the browser, and cleanup Stagehand instance

## Configuration

The Browserbase MCP server accepts the following command-line flags:

Flag | Description
---- | -----------
`--proxies` | Enable Browserbase proxies for the session
`--advancedStealth` | Enable Browserbase Advanced Stealth (Only for Scale Plan Users)
`--keepAlive` | Enable Browserbase Keep Alive Session
`--contextId <contextId>` | Specify a Browserbase Context ID to use
`--persist` | Whether to persist the Browserbase context (default: true)
`--port <port>` | Port to listen on for HTTP/SHTTP transport
`--host <host>` | Host to bind server to (default: localhost, use 0.0.0.0 for all interfaces)
`--cookies [json]` | JSON array of cookies to inject into the browser
`--browserWidth <width>` | Browser viewport width (default: 1024)
`--browserHeight <height>` | Browser viewport height (default: 768)
`--modelName <model>` | The model to use for Stagehand (default: gemini-2.0-flash)
`--modelApiKey <key>` | API key for the custom model provider (required when using custom models)
`--experimental` | Enable experimental features (default: false)

## Additional resources

- [Browserbase MCP Server Documentation](https://docs.browserbase.com/integrations/mcp/introduction)
- [Browserbase MCP Server Configuration](https://docs.browserbase.com/integrations/mcp/configuration)
- [Browserbase MCP Server Repository](https://github.com/browserbase/mcp-server-browserbase)
