# Tavily

The [Tavily MCP Server](https://github.com/tavily-ai/tavily-mcp) connects your
ADK agent to Tavily's AI-focused search, extraction, and crawling platform. This
tool gives your agent the ability to perform real-time web searches,
intelligently extract specific data from web pages, and crawl or create
structured maps of websites.

## Use cases

- **Real-Time Web Search**: Perform optimized, real-time web searches to get
  up-to-date information for your agent's tasks.

- **Intelligent Data Extraction**: Extract specific, clean data and content from
  any web page without needing to parse the full HTML.

- **Website Exploration**: Automatically crawl websites to explore content or
  create a structured map of a site's layout and pages.

## Prerequisites

- Sign up for a [Tavily account](https://app.tavily.com/) to obtain an API key.
  Refer to the
  [documentation](https://docs.tavily.com/documentation/quickstart) for more
  information.

## Use with agent

=== "Local MCP Server"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters

    TAVILY_API_KEY = "YOUR_TAVILY_API_KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="tavily_agent",
        instruction="Help users get information from Tavily",
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params = StdioServerParameters(
                        command="npx",
                        args=[
                            "-y",
                            "tavily-mcp@latest",
                        ],
                        env={
                            "TAVILY_API_KEY": TAVILY_API_KEY,
                        }
                    ),
                    timeout=30,
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

    TAVILY_API_KEY = "YOUR_TAVILY_API_KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="tavily_agent",
        instruction="""Help users get information from Tavily""",
        tools=[
            McpToolset(
                connection_params=StreamableHTTPServerParams(
                    url="https://mcp.tavily.com/mcp/",
                    headers={
                        "Authorization": f"Bearer {TAVILY_API_KEY}",
                    },
                ),
            )
        ],
    )
    ```

## Example usage

Once your agent is set up and running, you can interact with it through the
command-line interface or web interface. Here's a simple example:

**Sample agent prompt:**

> Find all documentation pages on tavily.com and provide instructions on how to get started with Tavily

The agent automatically calls multiple Tavily tools to provide comprehensive
answers, making it easy to explore websites and gather information without
manual navigation:

<img src="../../../assets/tools-tavily-screenshot.png">

## Available tools

Once connected, your agent gains access to Tavily's web intelligence tools:

Tool <img width="100px"/> | Description
---- | -----------
`tavily-search` | Execute a search query to find relevant information across the web.
​`tavily-extract` | Extract structured data from any web page. Extract text, links, and images from single pages or batch process multiple URLs efficiently.
​`tavily-map` | Traverses websites like a graph and can explore hundreds of paths in parallel with intelligent discovery to generate comprehensive site maps.
​`tavily-crawl` | Traversal tool that can explore hundreds of paths in parallel with built-in extraction and intelligent discovery.

## Additional resources

- [Tavily MCP Server Documentation](https://docs.tavily.com/documentation/mcp)
- [Tavily MCP Server Repository](https://github.com/tavily-ai/tavily-mcp)
