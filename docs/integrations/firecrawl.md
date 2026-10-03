---
catalog_title: Firecrawl
catalog_description: Search, scrape, and interact with the web to give agents live context
catalog_icon: /integrations/assets/firecrawl.png
catalog_tags: ["mcp"]
---

# Firecrawl MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Firecrawl MCP Server](https://github.com/firecrawl/firecrawl-mcp-server)
connects your ADK agent to [Firecrawl](https://www.firecrawl.dev/), the context
API to search, scrape, and interact with the web at scale. Search finds
sources, Scrape turns pages into clean markdown or JSON, and Interact reaches
information behind dynamic page actions. Your agent can call these tools using
natural language, for example "Find the three most recent posts about agent
memory and summarize each one".

The hosted server runs at `https://mcp.firecrawl.dev/v2/mcp` over streamable
HTTP. You can also run the server locally with `npx`.

## Use cases

- **Research with live sources**: Search the web for a topic, then scrape the
  pages that matter into markdown the agent can read and cite.

- **Structured data from a page**: Scrape a page and return JSON that matches
  a schema you define, for example pricing tiers, product specs, or contact
  details.

- **Content behind page actions**: Open a live browser session to click
  through menus, expand sections, or fill in forms, then read the content that
  only appears after those actions.

- **Whole-site ingestion**: Map a site's URLs and crawl the pages you need
  into a knowledge base or retrieval index.

## Prerequisites

- For Python, install ADK with the MCP extra:
  `pip install "google-adk[mcp]"`
- For the full tool set, create a
  [Firecrawl account](https://www.firecrawl.dev/signin) and generate an API
  key from the [Firecrawl dashboard](https://www.firecrawl.dev/app/api-keys)
- For the local server, install Node.js 22 or later

The hosted server also accepts connections without an API key. In that mode it
exposes `firecrawl_search`, `firecrawl_scrape`, and `firecrawl_parse` with
usage limits. To try it without a key, remove the `headers` argument from the
Remote MCP Server sample. Send your API key as a Bearer token to unlock the
full tool set.

## Use with agent

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        FIRECRAWL_API_KEY = "YOUR_FIRECRAWL_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="firecrawl_agent",
            instruction="Help users research topics and read web pages",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "firecrawl-mcp",
                            ],
                            env={
                                "FIRECRAWL_API_KEY": FIRECRAWL_API_KEY,
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
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        FIRECRAWL_API_KEY = "YOUR_FIRECRAWL_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="firecrawl_agent",
            instruction="Help users research topics and read web pages",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mcp.firecrawl.dev/v2/mcp",
                        headers={
                            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
                        },
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const FIRECRAWL_API_KEY = "YOUR_FIRECRAWL_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "firecrawl_agent",
            instruction: "Help users research topics and read web pages",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "firecrawl-mcp"],
                        env: {
                            FIRECRAWL_API_KEY: FIRECRAWL_API_KEY,
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const FIRECRAWL_API_KEY = "YOUR_FIRECRAWL_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "firecrawl_agent",
            instruction: "Help users research topics and read web pages",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.firecrawl.dev/v2/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${FIRECRAWL_API_KEY}`,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## Available tools

### Search and read

Tool | Description
---- | -----------
`firecrawl_search` | Search web, news, or image sources and return ranked results with highlights
`firecrawl_scrape` | Scrape one URL and return markdown, HTML, links, a screenshot, or JSON matching a schema
`firecrawl_map` | List the URLs under a website without fetching each page

### Crawl

Tool | Description
---- | -----------
`firecrawl_crawl` | Crawl a website from a starting URL, bounded by paths, depth, and page limit, and return the collected pages
`firecrawl_check_crawl_status` | Check the status, progress, and results of an existing crawl

### Interact and research

Tool | Description
---- | -----------
`firecrawl_interact` | Open a browser session on the live site to navigate, click, fill fields, or run browser code
`firecrawl_interact_stop` | Stop a live interact session and release its resources
`firecrawl_agent` | Start a research job that searches and reads across sources when the URLs are not known, and return its job ID
`firecrawl_agent_status` | Check progress of a research job or fetch its final JSON result

### Documents and developer sources

Tool | Description
---- | -----------
`firecrawl_parse` | Parse a PDF, Word, spreadsheet, or other document file into markdown or JSON
`firecrawl_developer_search` | Search public repositories, GitHub issues, merged pull requests, and code documentation for programming questions

The hosted server can't read local files. For `firecrawl_parse`, it returns an
upload command for the file instead, which the agent can't run with this
toolset alone. To parse local files, use the Local MCP Server.

The server also exposes tools for monitoring pages for changes, searching
research papers, browsing data providers, checking credit usage, and sending
feedback on results. See the
[Firecrawl MCP tools reference](https://docs.firecrawl.dev/mcp-server/tools)
for details on every tool.

## Configuration

The local server reads these environment variables:

- `FIRECRAWL_API_KEY`: Your Firecrawl API key. Required for the Firecrawl
  cloud API.
- `FIRECRAWL_API_URL` (optional): Base URL of a
  [self-hosted Firecrawl instance](https://docs.firecrawl.dev/contributing/self-host).
  Leave it unset to use the Firecrawl cloud API.

## Additional resources

- [Firecrawl MCP Server Documentation](https://docs.firecrawl.dev/mcp-server)
- [Firecrawl MCP Server Repository](https://github.com/firecrawl/firecrawl-mcp-server)
- [Firecrawl Documentation](https://docs.firecrawl.dev/)
