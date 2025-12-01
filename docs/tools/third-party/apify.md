# Apify

The [Apify MCP Server](https://github.com/apify/actors-mcp-server) allows AI
applications and agents to interact with the Apify platform. This functionality
enables your ADK agents to discover and run Actors from
[Apify Store](https://apify.com/store), access storages and results, and read
Apify documentation.

## Use cases

- **Actor Discovery**: Search and discover relevant Actors in the Apify Store to
  solve specific tasks.
- **Web Scraping & Automation**: Run Actors to scrape websites, extract data,
  and automate web workflows.
- **RAG & Knowledge Retrieval**: Use the RAG Web Browser Actor to retrieve and
  process information from the web for your agent.

## Prerequisites

- [Sign up](https://console.apify.com/sign-up) for an Apify account.
- Get your API token from the [Apify Console](https://console.apify.com). Refer
  to the [documentation](https://docs.apify.com/platform/integrations/api) for
  more information.

## Use with agent

=== "Local MCP Server"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters

    APIFY_TOKEN = "YOUR_APIFY_TOKEN"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="apify_agent",
        instruction="Help users scrape data and run Apify Actors",
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command="npx",
                        args=[
                            "-y",
                            "@apify/actors-mcp-server",
                            # (Optional) Customize which tools to enable
                            # "--tools=actors,docs,apify/web-scraper",
                        ],
                        env={
                            "APIFY_TOKEN": APIFY_TOKEN,
                        }
                    ),
                    timeout=300,
                ),
            )
        ],
    )
    ```

=== "Remote MCP Server"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

    APIFY_TOKEN = "YOUR_APIFY_TOKEN"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="apify_agent",
        instruction="Help users scrape data and run Apify Actors",
        tools=[
            McpToolset(
                connection_params=StreamableHTTPServerParams(
                    url="https://mcp.apify.com",
                    # (Optional) Customize which tools to enable
                    # url="https://mcp.apify.com?tools=actors,docs,apify/web-scraper",
                    headers={
                        "Authorization": f"Bearer {APIFY_TOKEN}",
                    },
                ),
            )
        ],
    )
    ```

## Available tools

Tool | Description
---- | -----------
`search-actors` | Search for Actors in the Apify Store
`fetch-actor-details` | Get detailed information about a specific Actor
`call-actor` | Run an Actor and wait for it to finish
`get-actor-run` | Get information about a specific Actor run
`get-actor-run-list` | List Actor runs
`get-actor-log` | Get logs from an Actor run
`get-dataset` | Get information about a dataset
`get-dataset-items` | Get items from a dataset
`get-key-value-store` | Get information about a key-value store
`get-key-value-store-record` | Get a record from a key-value store
`add-actor` | Add an Actor as a tool to the agent (Dynamic tool discovery)
`search-apify-docs` | Search Apify documentation
`fetch-apify-docs` | Read Apify documentation pages

## Configuration

You can customize which tools are available by adding parameters to the server
URL.

- **Default tools**: `actors`, `docs`, and `apify/rag-web-browser` are loaded by
  default.
- **Specific tools**: You can specify tools using the `tools` CLI parameter
  (local MCP server) or the `tools` query parameter (remote MCP server).

Example URL for specific tools:

```
https://mcp.apify.com?tools=apify/instagram-scraper,apify/google-search-scraper
```

## Additional resources

- [Apify MCP Server Documentation](https://docs.apify.com/platform/integrations/mcp)
- [Apify MCP Server Repository](https://github.com/apify/apify-mcp-server)
