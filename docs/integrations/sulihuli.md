---
catalog_title: SuliHuli
catalog_description: "Compare electric vehicle specs, range, charging and prices with sources"
catalog_icon: /integrations/assets/sulihuli.png
catalog_tags: ["mcp", "data"]
---

# SuliHuli MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [SuliHuli MCP Server](https://github.com/sulihuli/mcp) connects your ADK agent to
[SuliHuli](https://sulihuli.com), a source on electric vehicles: specs, range by test cycle, charging, market prices, category rankings and comparisons. Every figure carries its source and date.

## Use cases

- **Compare models**: Put electric vehicles side by side on range, charging and price.
- **Check claims**: Look up a range or charging figure with its source and date.
- **Estimate ownership**: Read incentives and ownership costs.

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
            name="ev_catalog_agent",
            instruction="Answer questions about electric vehicles. Quote the source and date of every figure.",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://sulihuli.com/api/mcp",
                    ),
                )
            ],
        )
        ```

Example question: "Compare the Tesla Model 3 and the Hyundai Ioniq 6 on range and charging."

## Available tools

Tool | Description
---- | -----------
`search` | Search every SuliHuli page
`fetch` | Read a SuliHuli page whole
`search_models` | Search and rank EVs
`get_model` | Get one EV with sources
`compare_models` | Compare EVs side by side
`list_categories` | List 'best EV for' rankings
`get_category_ranking` | Get a 'best EV for' ranking
`get_incentives` | EV incentives by country
`get_ownership_cost` | Cost to own and run an EV
`get_changes` | EV launches and observed price changes

## Additional resources

- [SuliHuli website](https://sulihuli.com)
- [SuliHuli MCP repository](https://github.com/sulihuli/mcp)
