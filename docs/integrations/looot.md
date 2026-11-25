---
catalog_title: looot
catalog_description: Search, price and run 2,500+ data API endpoints with one key and one balance
catalog_icon: /integrations/assets/looot.png
catalog_tags: ["data", "mcp"]
---

# looot MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[looot](https://looot.ai) gives an agent one key and one prepaid balance for
2,500+ data API endpoints from 90+ providers: work emails, phone numbers,
company and people search, Google results, web pages, news, LinkedIn profiles
and local businesses. The hosted [looot MCP server](https://docs.looot.ai)
lets your ADK agent search the catalog, see an endpoint's price before it
runs, and pay per call. A failed call costs nothing.

## Use cases

- **Lead enrichment**: Find and verify a work email, or look up a company and
  its people, from a name and a domain.
- **Research**: Pull Google results, web pages and news into an agent's
  context.
- **Price-aware agents**: Inspect an endpoint's price first, then decide
  whether to run it.

## Prerequisites

- A looot account. Sign up at [looot.ai](https://looot.ai/auth/sign-up).
- An agent token. In looot, open Settings, then the Agent tokens tab, and tick
  `catalog.read`, `runs.read`, `runs.execute` and `usage.read`.
- A prepaid balance for paid runs (top up from $5). Searching the catalog and
  inspecting an endpoint need no balance.

## Use with agent

=== "Python"

    === "Remote MCP Server"

        ```python
        import os

        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        LOOOT_TOKEN = os.environ["LOOOT_TOKEN"]

        root_agent = Agent(
            model="gemini-flash-latest",
            name="looot_agent",
            instruction=(
                "Find the right data endpoint for the task with search_catalog, "
                "check its price with inspect, and only then run it."
            ),
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://api.looot.ai/mcp",
                        headers={"Authorization": f"Bearer {LOOOT_TOKEN}"},
                    ),
                    tool_filter=["search_catalog", "inspect", "run", "runs_get", "balance"],
                )
            ],
        )
        ```

=== "TypeScript"

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const LOOOT_TOKEN = process.env.LOOOT_TOKEN;

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "looot_agent",
            instruction:
                "Find the right data endpoint for the task with search_catalog, " +
                "check its price with inspect, and only then run it.",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://api.looot.ai/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${LOOOT_TOKEN}`,
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
`search_catalog` | Search endpoints by the task you want done
`inspect` | Show an endpoint's inputs, outputs and price
`run` | Run an endpoint and pay per call from the prepaid balance
`runs_get` | Fetch the status and result of a run
`runs_list` | List recent runs
`balance` | Show the prepaid balance
`top_up` | Get a link to add balance

The full tool list is in the [looot llms.txt](https://api.looot.ai/llms.txt).

## Resources

- [looot documentation](https://docs.looot.ai)
- [looot MCP server repository](https://github.com/loootai/looot-mcp)
- [Privacy policy](https://looot.ai/privacy) and [support](https://looot.ai/contact)
