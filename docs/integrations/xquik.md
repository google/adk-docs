---
catalog_title: Xquik
catalog_description: Search X posts, read profiles, and monitor accounts from your agent
catalog_icon: /integrations/assets/xquik.png
catalog_tags: ["mcp", "data"]
---

# Xquik MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [Xquik MCP Server](https://docs.xquik.com/mcp/overview) connects your ADK
agent to [Xquik](https://xquik.com), an X Twitter data API. Your agent can
search posts, read profiles, export followers, and monitor accounts. Xquik is an
independent third-party service and is not affiliated with X Corp.

## Use cases

- **Social research**: Search recent posts on a topic and summarize what people
  are saying.

- **Account analysis**: Read a profile, its recent posts, and its followers.

- **Monitoring**: Track accounts and keywords, then review new matches in your
  agent.

- **Reviewed publishing**: Draft a post, then send it through a connected X
  account after a person approves it.

## Prerequisites

- Create an [Xquik account](https://xquik.com)
- Create an API key on the [account page](https://dashboard.xquik.com/account)
- Connect an X account if your agent needs private reads or writes

## Use with agent

=== "Python"

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

        XQUIK_API_KEY = "YOUR_XQUIK_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="xquik_agent",
            instruction="Help users search X posts and read profiles with Xquik",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://xquik.com/mcp",
                        headers={
                            "Authorization": f"Bearer {XQUIK_API_KEY}",
                        },
                    ),
                )
            ],
        )
        ```

## Available tools

Tool | Description
---- | -----------
`docs` | Searches the Xquik documentation
`search` | Finds the right API operation for a task
`execute` | Runs JavaScript that sends requests to the Xquik API
`whoami` | Returns the Xquik account this connection uses

`docs`, `search`, and `whoami` are free. `execute` charges the price of each
route it calls, and it can run every operation your key allows.

## Additional resources

- [Xquik MCP Documentation](https://docs.xquik.com/mcp/overview)
- [Xquik ADK Guide](https://docs.xquik.com/guides/google-adk)
- [Xquik MCP Repository](https://github.com/Xquik-dev/xquik-mcp)
