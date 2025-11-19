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

- Create an [API Key](https://dashboard.scrapegraphai.com/register/) in
  ScrapeGraphAI. Refer to the
  [documentation](https://docs.scrapegraphai.com/api-reference/introduction) for more information.
- Install the [ScrapeGraphAI MCP server
  package](https://pypi.org/project/scrapegraph-mcp/) (requires Python 3.13 or
  higher):

    ```console
    pip install scrapegraph-mcp
    ```

## Use with agent

=== "Local MCP Server"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters

    SGAI_API_KEY = "YOUR_SCRAPEGRAPHAI_API_KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="scrapegraph_assistant_agent",
        instruction="""Help the user with web scraping and data extraction using
                      ScrapeGraph AI. You can convert webpages to markdown, extract
                      structured data using AI, perform web searches, crawl
                      multiple pages, and automate complex scraping workflows.""",
        tools=[
            MCPToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        # The following CLI command is available
                        # from `pip install scrapegraph-mcp`
                        command="scrapegraph-mcp",
                        env={
                            "SGAI_API_KEY": SGAI_API_KEY,
                        },
                    ),
                    timeout=300,
                ),
            # Optional: Filter which tools from the MCP server are exposed
            # tool_filter=["markdownify", "smartscraper", "searchscraper"]
            ),
        ],
    )
    ```

## Available tools

Tool <img width="200px"/> | Description
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
