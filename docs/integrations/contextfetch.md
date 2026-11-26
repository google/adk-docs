---
catalog_title: ContextFetch
catalog_description: Search the web and read pages as Markdown for your agent
catalog_icon: /integrations/assets/contextfetch.png
catalog_tags: ["mcp"]
---

# ContextFetch MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [ContextFetch MCP server](https://github.com/lachy3433/contextfetch-mcp)
connects your ADK agent to the [ContextFetch](https://contextfetch.dev) web
search API. Search results come back as Markdown, and by default each result
holds only the passages of the page that are relevant to the query. The server
can also read any public URL as Markdown, run several searches in one call, and
crawl or map a site.

The server is hosted at `https://api.contextfetch.dev/mcp` over streamable
HTTP. It is also published on npm as `@contextfetch/mcp` to run locally over
stdio.

## Use cases

- **Answer questions from the web**: Search and give the model only the
  relevant passages of each result, with titles and URLs to cite.

- **Read documentation and articles**: Fetch a known URL as Markdown, or only
  the parts of it that answer a question.

- **Gather sources for a report**: Run several searches in one call and get the
  pages ranked together, with numbered sources.

## Prerequisites

- A working [ADK installation](/get-started/installation/). In Python, install
  the MCP extra with `pip install "google-adk[mcp]"`. In TypeScript, install
  the MCP SDK next to ADK with `npm install @google/adk @modelcontextprotocol/sdk`.
- Optional: a ContextFetch API key. Without a key, requests use a small daily
  keyless allowance per IP address. The `contextfetch_get_free_key` tool returns
  a starter key, and keys are listed at
  [contextfetch.dev](https://contextfetch.dev).
- For the local server: [Node.js](https://nodejs.org/) 18 or later.

## Use with agent

The examples pass `tool_filter` to expose only the search and read tools. The
server also has account tools, such as `contextfetch_auto_reload`, which changes
the key's billing settings, so leave them out unless the agent needs them.

=== "Python"

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        CONTEXTFETCH_API_KEY = "YOUR_CONTEXTFETCH_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="contextfetch_agent",
            instruction="Answer questions using web search. Cite the URLs you use.",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://api.contextfetch.dev/mcp",
                        # Leave out the headers to use the keyless allowance.
                        headers={"Authorization": f"Bearer {CONTEXTFETCH_API_KEY}"},
                        timeout=30,
                    ),
                    tool_filter=[
                        "contextfetch_search",
                        "contextfetch_extract_url",
                        "contextfetch_research",
                        "contextfetch_answer",
                    ],
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

        CONTEXTFETCH_API_KEY = "YOUR_CONTEXTFETCH_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="contextfetch_agent",
            instruction="Answer questions using web search. Cite the URLs you use.",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=["-y", "@contextfetch/mcp"],
                            env={"CONTEXTFETCH_API_KEY": CONTEXTFETCH_API_KEY},
                        ),
                        timeout=60,
                    ),
                    tool_filter=[
                        "contextfetch_search",
                        "contextfetch_extract_url",
                        "contextfetch_research",
                        "contextfetch_answer",
                    ],
                )
            ],
        )
        ```

=== "TypeScript"

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const CONTEXTFETCH_API_KEY = "YOUR_CONTEXTFETCH_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "contextfetch_agent",
            instruction: "Answer questions using web search. Cite the URLs you use.",
            tools: [
                new MCPToolset(
                    {
                        type: "StreamableHTTPConnectionParams",
                        url: "https://api.contextfetch.dev/mcp",
                        // Leave out transportOptions to use the keyless allowance.
                        transportOptions: {
                            requestInit: {
                                headers: {
                                    Authorization: `Bearer ${CONTEXTFETCH_API_KEY}`,
                                },
                            },
                        },
                    },
                    [
                        "contextfetch_search",
                        "contextfetch_extract_url",
                        "contextfetch_research",
                        "contextfetch_answer",
                    ],
                ),
            ],
        });

        export { rootAgent };
        ```

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const CONTEXTFETCH_API_KEY = "YOUR_CONTEXTFETCH_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "contextfetch_agent",
            instruction: "Answer questions using web search. Cite the URLs you use.",
            tools: [
                new MCPToolset(
                    {
                        type: "StdioConnectionParams",
                        serverParams: {
                            command: "npx",
                            args: ["-y", "@contextfetch/mcp"],
                            env: {
                                CONTEXTFETCH_API_KEY: CONTEXTFETCH_API_KEY,
                            },
                        },
                    },
                    [
                        "contextfetch_search",
                        "contextfetch_extract_url",
                        "contextfetch_research",
                        "contextfetch_answer",
                    ],
                ),
            ],
        });

        export { rootAgent };
        ```

## Available tools

Tool | Description
---- | -----------
`contextfetch_search` | Search the web. Each result has its title, URL and the passages relevant to the query.
`contextfetch_extract_url` | Read a public URL as Markdown. With `query`, returns only the relevant passages.
`contextfetch_find_similar` | Find pages similar to a URL, excluding its own domain.
`contextfetch_research` | Run up to 5 searches in one call and return the pages ranked together as numbered sources.
`contextfetch_deep_research` | A deeper research call that also searches sub-topics and pages linked from the results.
`contextfetch_answer` | Return the passages that best answer a question, quoted from the pages with numbered sources.
`contextfetch_crawl` | Crawl one site from a start URL and return each page as Markdown. Obeys robots.txt.
`contextfetch_map` | List a site's URLs from its sitemaps and links without fetching the pages.
`contextfetch_balance` | Show the API key's remaining credits.
`contextfetch_get_free_key` | Get a free starter API key, one per network.
`contextfetch_auto_reload` | Turn automatic credit top-ups on or off for the API key.
`search` | Search the web and return result IDs, for clients that expect a `search` and `fetch` pair.
`fetch` | Fetch the full text of a `search` result by its ID.

## Additional resources

- [ContextFetch MCP server repository](https://github.com/lachy3433/contextfetch-mcp)
- [`@contextfetch/mcp` on npm](https://www.npmjs.com/package/@contextfetch/mcp)
- [ContextFetch API reference](https://contextfetch.dev/docs/reference)
