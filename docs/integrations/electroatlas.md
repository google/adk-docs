---
catalog_title: ElectroAtlas
catalog_description: "Electric cars in Russia: rouble prices, winter range, dealers and import rules"
catalog_icon: /integrations/assets/electroatlas.png
catalog_tags: ["mcp", "data"]
---

# ElectroAtlas MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [ElectroAtlas MCP Server](https://github.com/electroatlas/mcp) connects your ADK agent to
[ElectroAtlas](https://electroatlas.ru), a source on electric cars and plug-in hybrids sold in Russia: rouble prices with sources, rated and winter range, sales, dealers, import rules and fees. Answers are in Russian and link to the catalog.

## Use cases

- **Shortlist a car**: Find electric cars and hybrids that fit a budget, a daily distance and winter conditions.
- **Compare models**: Put two models side by side on price and range, with the sources.
- **Check import costs**: Read the import rules and calculate the fees.

## Prerequisites

- No account or API key

## Use with agent

=== "Python"

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

        root_agent = Agent(
            model="gemini-flash-latest",
            name="ev_russia_agent",
            instruction="Help the user choose an electric car in Russia. Quote sources.",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://electroatlas.ru/mcp",
                    ),
                )
            ],
        )
        ```

Example question: "Compare Zeekr 001 and Li Auto L7 on price and winter range."

## Available tools

Tool | Description
---- | -----------
`search` | Search the site
`fetch` | Read a page in full
`search_models` | Search electric cars
`get_model` | Model card
`compare_models` | Compare two models
`get_sales` | Sales figures
`find_dealers` | Find dealers
`list_regulations` | List rules and regulations
`get_regulation` | Read one regulation
`calc_import_fees` | Calculate import fees
`get_ranking` | Car ranking
`get_changes` | Recent changes
`pick_car` | Pick a car for a driver
`calc_ownership` | Cost of ownership

## Additional resources

- [ElectroAtlas website](https://electroatlas.ru)
- [ElectroAtlas MCP repository](https://github.com/electroatlas/mcp)
