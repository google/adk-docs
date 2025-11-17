# ScrapeGraphAI

The
[ScrapeGraphAI MCP Server](https://github.com/ScrapeGraphAI/scrapegraph-mcp)
connects your ADK agent to [ScrapeGraphAI](https://scrapegraphai.com/). This
integration enables your agent to extract structured data using natural language
prompts, handle dynamic content like infinite scrolling, and convert complex
webpages into clean, usable JSON or Markdown.

## Use cases

- **Scalable Extraction & Crawling**: Extract structured data from single pages
  or crawl entire websites, leveraging AI to handle dynamic content, infinite
  scrolling, and large-scale asynchronous operations.

- **Research and Summarization**: Execute AI-powered web searches to research
  topics, aggregate data from multiple sources, and summarize findings.

- **Agentic Workflows**: Run advanced agentic scraping workflows with
  customizable steps, complex navigation (like authentication), and structured
  output schemas.

## Prerequisites

- Create an [API Key](https://dev.agentql.com/sign-in) in AgentQL. Refer to the
  [documentation](https://docs.agentql.com/quick-start) for more information.

## Use with agent

=== "Local MCP Server"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
    from mcp import StdioServerParameters

    SCRAPEGRAPHAI_API_KEY = "YOUR_SCRAPEGRAPHAI_API_KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="agentql_agent",
        instruction="Help users get information from AgentQL",
        tools=[
            MCPToolset(
                connection_params=StdioConnectionParams(
                    server_params = StdioServerParameters(
                        command="npx",
                        args=[
                            "-y",
                            "@scrapegraphai/mcp-server",
                        ],
                        env={
                            "SGAI_API_KEY": SCRAPEGRAPHAI_API_KEY,
                        }
                    ),
                    timeout=300,
                ),
            )
        ],
    )
    ```

## Available tools

Tool <img width="100px"/> | Description
---- | -----------
`markdownify` | Transform any webpage into clean, structured markdown format
`smartscraper` | Leverage AI to extract structured data from any webpage with support for infinite scrolling
`searchscraper` | Execute AI-powered web searches with structured, actionable results
`scrape` | Basic scraping endpoint to fetch page content with optional heavy JavaScript rendering
`sitemap` | Extract sitemap URLs and structure for any website
`smartcrawler_initiate` | Initiate intelligent multi-page web crawling (asynchronous operation)
`smartcrawler_fetch_results` | Retrieve results from asynchronous crawling operations
`agentic_scrapper` | Run advanced agentic scraping workflows with customizable steps and structured output schemas

## Additional resources

- [ScrapeGraphAI MCP Server Documentation](https://docs.scrapegraphai.com/services/mcp-server)
- [ScrapeGraphAI MCP Server Repository](https://github.com/ScrapeGraphAI/scrapegraph-mcp)
