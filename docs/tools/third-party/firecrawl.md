# Firecrawl

## Overview

[Firecrawl](https://www.firecrawl.dev/) is an API service that takes a URL,
crawls it, and converts it into clean markdown or structured data. Crawls all
accessible subpages and gives you clean data for each.

## Features

- Efficient web scraping, crawling, and content discovery from any website
- Advanced search capabilities and intelligent content extraction for structured and unstructured data
- Facilitates deep research and high-volume batch scraping with robust performance
- Flexible deployment options, including cloud-based services and self-hosted instances
- Optimized for modern web environments with streamable HTTP support for faster data processing

## Prerequisites

* Obtain an [API key for Firecrawl](https://firecrawl.dev/app/api-keys)

## Usage with ADK

=== "Local MCP Server"

    ```python
    from google.adk.agents.llm_agent import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
    from mcp import StdioServerParameters

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="firecrawl_agent",
        description="A helpful assistant for scraping websites with Firecrawl",
        instruction="Help the user search for website content",
        tools=[
            MCPToolset(
                connection_params=StdioConnectionParams(
                    server_params = StdioServerParameters(
                        command="npx",
                        args=[
                            "-y",
                            "firecrawl-mcp",
                        ],
                        env={
                            "FIRECRAWL_API_KEY": "YOUR-API-KEY",
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
    from google.adk.agents.llm_agent import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

    FIRECRAWL_API_KEY = "YOUR-API-KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="firecrawl_agent",
        description="A helpful assistant for scraping websites with Firecrawl",
        instruction="Help the user search for website content",
        tools=[
            MCPToolset(
                connection_params=StreamableHTTPServerParams(
                    url=f"https://mcp.firecrawl.dev/{FIRECRAWL_API_KEY}/v2/mcp",
                ),
            )
        ],
    )
    ```

## Available tools

Tool | Name | Description
---- | ---- | -----------
Scrape Tool | `firecrawl_scrape` | Scrape content from a single URL with advanced options
Batch Scrape Tool | `firecrawl_batch_scrape` | Scrape multiple URLs efficiently with built-in rate limiting and parallel processing
Check Batch Status | `firecrawl_check_batch_status` | Check the status of a batch operation
Map Tool | `firecrawl_map` | Map a website to discover all indexed URLs on the site
Search Tool | `firecrawl_search` | Search the web and optionally extract content from search results
Crawl Tool | `firecrawl_crawl` | Start an asynchronous crawl with advanced options
Check Crawl Status | `firecrawl_check_crawl_status` | Check the status of a crawl job
Extract Tool | `firecrawl_extract` | Extract structured information from web pages using LLM capabilities. Supports both cloud AI and self-hosted LLM extraction

## Configuration

Required:

- `FIRECRAWL_API_KEY`: Your Firecrawl API key
    - Required when using cloud API (default)
    - Optional when using self-hosted instance with `FIRECRAWL_API_URL`

Firecrawl API URL (optional):

- `FIRECRAWL_API_URL` (Optional): Custom API endpoint for self-hosted instances
    - Example: `https://firecrawl.your-domain.com`
    - If not provided, the cloud API will be used (requires API key)

Retry configuration (optional):

- `FIRECRAWL_RETRY_MAX_ATTEMPTS`: Maximum number of retry attempts (default: 3)
- `FIRECRAWL_RETRY_INITIAL_DELAY`: Initial delay in milliseconds before first retry (default: 1000)
- `FIRECRAWL_RETRY_MAX_DELAY`: Maximum delay in milliseconds between retries (default: 10000)
- `FIRECRAWL_RETRY_BACKOFF_FACTOR`: Exponential backoff multiplier (default: 2)

Credit usage monitoring (optional):

- `FIRECRAWL_CREDIT_WARNING_THRESHOLD`: Credit usage warning threshold (default: 1000)
- `FIRECRAWL_CREDIT_CRITICAL_THRESHOLD`: Credit usage critical threshold (default: 100)

## Additional resources

- [Firecrawl MCP Server Documentation](https://docs.firecrawl.dev/mcp-server)
- [Firecrawl Use Cases](https://docs.firecrawl.dev/use-cases/overview)
- [Firecrawl Advanced Scraping Guide](https://docs.firecrawl.dev/advanced-scraping-guide)
