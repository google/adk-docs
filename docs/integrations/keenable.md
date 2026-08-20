---
catalog_title: Keenable
catalog_description: Search the web and read pages as markdown, no API key
catalog_icon: /integrations/assets/keenable.png
catalog_tags: ["search", "mcp"]
---

# Keenable MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Keenable MCP server](https://docs.keenable.ai/mcp-server) connects your ADK
agent to [Keenable](https://keenable.ai), a web search API built for agents. The
server is hosted and remote, so there is nothing to install or run, and it
answers without an account: an API key is optional and only raises rate limits.

Each search result carries the extracted text of the page, not only a title and
a link, so the agent can answer from the search call itself and fetch a full
page only when it needs one.

## Use cases

- **Ground answers in current information**: Look up events, prices, or releases
  that postdate the model's training data, and cite the sources used.

- **Research across several sources**: Search once, then read the pages worth
  reading in full to compare what they say.

- **Read a page the user names**: Turn a URL into clean markdown for
  summarizing, extraction, or question answering.

## Prerequisites

- A working [ADK installation](/get-started/installation/). In Python, ADK's MCP
  classes need the `mcp` extra, so install it with `pip install "google-adk[mcp]"`.
- No Keenable account. An optional API key from the
  [Keenable console](https://app.keenable.ai/console) raises the rate limits on
  the same endpoint.

## Use with agent

=== "Python"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

    root_agent = Agent(
        model="gemini-flash-latest",
        name="keenable_agent",
        instruction=(
            "Answer questions that need current information. Use"
            " search_web_pages to search the web, fetch_page_content to read a"
            " specific URL, and cite the sources you used."
        ),
        tools=[
            McpToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url="https://api.keenable.ai/mcp",
                    headers={"X-Keenable-Title": "ADK"},
                ),
            )
        ],
    )
    ```

=== "TypeScript"

    ```typescript
    import { LlmAgent, MCPToolset } from "@google/adk";

    const rootAgent = new LlmAgent({
        model: "gemini-flash-latest",
        name: "keenable_agent",
        instruction:
            "Answer questions that need current information. Use search_web_pages to search the web, fetch_page_content to read a specific URL, and cite the sources you used.",
        tools: [
            new MCPToolset({
                type: "StreamableHTTPConnectionParams",
                url: "https://api.keenable.ai/mcp",
                transportOptions: {
                    requestInit: {
                        headers: { "X-Keenable-Title": "ADK" },
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
`search_web_pages` | Search the web and return ranked results, each with the page text, URL, and publication date
`fetch_page_content` | Fetch a single URL and return the page as markdown

The search tool also accepts a `site` filter, publication and indexing date
ranges, a result count, and a per-result text budget. The fetch tool accepts a
character budget and an optional extraction instruction, which returns only the
answer to that instruction instead of the whole page.

## Configuration

Both headers below are optional, and neither is needed for the server to
respond.

Header | Purpose
------ | -------
`X-API-Key` | A Keenable API key. Raises the rate limits; the endpoint and the results are the same without it.
`X-Keenable-Title` | Names the calling application in Keenable's request logs.

## Additional resources

- [Keenable MCP server documentation](https://docs.keenable.ai/mcp-server)
- [Keenable API reference](https://docs.keenable.ai/api-reference)
- [Keenable MCP server repository](https://github.com/keenableai/keenable-mcp)
