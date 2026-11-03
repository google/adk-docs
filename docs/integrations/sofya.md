---
catalog_title: Sofya
catalog_description: Search the web, read pages as markdown, and run cited research
catalog_icon: /integrations/assets/sofya.png
catalog_tags: ["mcp", "search"]
---

# Sofya MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Sofya MCP server](https://github.com/sofya-co/sofya-mcp) connects your ADK
agent to [Sofya](https://sofya.co), a web search and page reading service
with its own search index. Your agent can search the web, read pages and
documents as markdown, pull specific facts out of a page, and run multi-source
research that returns a report with citations.

The server is hosted at `https://mcp.sofya.co/mcp` over streamable HTTP, so
there is nothing to install or run locally. The agent authenticates with a
Sofya API key sent as a bearer token.

## Use cases

- **Current information**: Answer questions that need recent facts, such as
  release dates, prices, or news, from live search results that include page
  content rather than only snippets.

- **Read a link**: Turn a URL into clean markdown, including PDF, Word, Excel,
  PowerPoint, and EPUB files, so the agent can summarize or quote it.

- **Pull specific facts**: Ask a question about one page and get back only the
  answer, for example a product's specifications or a company's address.

- **Multi-source research**: Break an open question into several searches,
  read the sources, and return a report with citations.

## Prerequisites

- A Sofya API key. Sign in to the
  [Sofya dashboard](https://sofya.co/dashboard) and copy your key. Usage is
  billed in credits; see [pricing](https://sofya.co/pricing).
- A [Gemini API key](https://aistudio.google.com/apikey) for the agent's model.

## Installation

=== "Python"

    Install ADK with the `mcp` extra, which ADK's MCP classes need:

    ```bash
    pip install "google-adk[mcp]"
    ```

=== "TypeScript"

    ```bash
    npm install @google/adk
    ```

## Use with agent

Set your API keys as environment variables:

```bash
export SOFYA_API_KEY="<your-sofya-api-key>"
export GOOGLE_API_KEY="<your-gemini-api-key>"
```

=== "Python"

    === "Remote MCP Server"

        ```python
        import os

        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        root_agent = Agent(
            model="gemini-flash-latest",
            name="sofya_agent",
            instruction=(
                "Answer questions using the Sofya tools to search the web and "
                "read pages. Cite the URLs you used."
            ),
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mcp.sofya.co/mcp",
                        headers={
                            "Authorization": f"Bearer {os.environ['SOFYA_API_KEY']}"
                        },
                        timeout=30,
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "sofya_agent",
            instruction:
                "Answer questions using the Sofya tools to search the web and " +
                "read pages. Cite the URLs you used.",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.sofya.co/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${process.env.SOFYA_API_KEY}`,
                            },
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
`search` | Search the web and return ranked results with extracted page content. Supports domain filters, a news topic, freshness, and an optional short answer
`fetch` | Fetch up to 10 URLs as markdown, including PDF, DOCX, XLSX, PPTX, and EPUB documents
`extract` | Fetch a page and return the information a prompt asks for
`research` | Run several searches on a question, read the sources, and return a report with citations
`get_balance` | Return the account's remaining credits
`buy_credits` | Return a payment link for a credit top-up. It does not charge anything

## Configuration

To expose only some of the tools, pass `tool_filter` in Python or the second
constructor argument in TypeScript. For example, to keep only the read-only web
tools:

=== "Python"

    ```python
    McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url="https://mcp.sofya.co/mcp",
            headers={"Authorization": f"Bearer {os.environ['SOFYA_API_KEY']}"},
            timeout=30,
        ),
        tool_filter=["search", "fetch", "extract", "research"],
    )
    ```

=== "TypeScript"

    ```typescript
    new MCPToolset(
        {
            type: "StreamableHTTPConnectionParams",
            url: "https://mcp.sofya.co/mcp",
            transportOptions: {
                requestInit: {
                    headers: { Authorization: `Bearer ${process.env.SOFYA_API_KEY}` },
                },
            },
        },
        ["search", "fetch", "extract", "research"],
    );
    ```

## Additional resources

- [Sofya documentation](https://sofya.co/docs)
- [Sofya MCP server repository](https://github.com/sofya-co/sofya-mcp)
- [Get a Sofya API key](https://sofya.co/dashboard)
- [Sofya pricing](https://sofya.co/pricing)
