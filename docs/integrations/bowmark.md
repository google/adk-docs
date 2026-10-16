---
catalog_title: Bowmark
catalog_description: Do things on live websites: prices, availability, quotes, bookings, anything behind a form or login.
catalog_icon: /integrations/assets/bowmark.png
catalog_tags: ["mcp"]
---

# Bowmark MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Bowmark](https://bowmark.ai) connects your ADK agent to the parts of the web that have
no public API: search boxes, filters, quote forms, product configurators, availability
lookups, checkout and booking flows, and pages behind a login. Instead of driving a
browser page by page, your agent reads a typed function library over the Bowmark MCP
server and writes a short script against it; Bowmark runs that script against the live
sites and returns structured data.

## Use cases

- **Price and availability lookups**: Check a price, a shipping quote, or whether
  something is in stock on a live site, in one call.

- **Fill out a form on the agent's behalf**: Submit a quote request, a configurator, or
  a booking flow and get back structured results instead of raw HTML.

- **Work across several sites at once**: One script can fan out across multiple sites
  in parallel, which a step-by-step browser session cannot do.

## Prerequisites

- Create a [Bowmark account](https://bowmark.ai/sign-up) and generate an API key at
  [bowmark.ai/dashboard/keys](https://bowmark.ai/dashboard/keys). Every account gets
  $10 of usage free each month.

## Use with agent

The agent connects to the hosted Bowmark MCP server over streamable HTTP and
authenticates with your API key as a bearer token.

=== "Python"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

    BOWMARK_API_KEY = "YOUR_BOWMARK_API_KEY"

    root_agent = Agent(
        model="gemini-flash-latest",
        name="bowmark_agent",
        instruction=(
            "Use the Bowmark tools to look up prices, availability, and other "
            "live-website data, and to fill out forms such as quotes and bookings."
        ),
        tools=[
            McpToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url="https://api.bowmark.ai/mcp",
                    headers={"Authorization": f"Bearer {BOWMARK_API_KEY}"},
                ),
            )
        ],
    )
    ```

=== "TypeScript"

    ```typescript
    import { LlmAgent, MCPToolset } from "@google/adk";

    const BOWMARK_API_KEY = "YOUR_BOWMARK_API_KEY";

    const rootAgent = new LlmAgent({
        model: "gemini-flash-latest",
        name: "bowmark_agent",
        instruction:
            "Use the Bowmark tools to look up prices, availability, and other " +
            "live-website data, and to fill out forms such as quotes and bookings.",
        tools: [
            new MCPToolset({
                type: "StreamableHTTPConnectionParams",
                url: "https://api.bowmark.ai/mcp",
                transportOptions: {
                    requestInit: {
                        headers: {
                            Authorization: `Bearer ${BOWMARK_API_KEY}`,
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
`get_library` | Discover the typed capability functions available for a task (search for the right one by plain-language query)
`run` | Run a short JavaScript script against the discovered capabilities on the live sites and return structured data

## Additional resources

- [Bowmark installation guide](https://bowmark.ai/docs/installation)
- [Bowmark quickstart](https://bowmark.ai/docs/quickstart)
- [Bowmark pricing](https://bowmark.ai/docs/pricing)
