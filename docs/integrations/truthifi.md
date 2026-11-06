---
catalog_title: Truthifi
catalog_description: One verified household record for your agent: accounts, holdings, fees and Score
catalog_icon: /integrations/assets/truthifi.png
catalog_tags: ["mcp"]
---

# Truthifi MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Truthifi MCP Server](https://truthifi.com/mcp-tools) connects your ADK agent to
[Truthifi](https://truthifi.com/), the financial hub for families, advisors and AI
agents. It brings one verified household record into your agent: accounts, activity,
holdings, fees, performance, cash flow, the advisors on the accounts, financial
diagnostics, and the Truthifi Score with the findings behind it, from 18,000+
supported institutions. The agent can't move money, place trades or change
anything at the user's bank or brokerage.

## Use cases

- **Fee review**: Find advisory, fund, margin and commission fees per account.
- **Portfolio analysis**: Holdings on any date, allocation by asset class, sector and market cap, and single-stock concentration including fund look-through.
- **Performance and health**: Returns against a similar benchmark, plus the Truthifi Score and the findings behind it.

## Prerequisites

- A [Truthifi account](https://truthifi.com) with at least one linked account (free plan available; some tools need a paid plan)
- Node.js (for `mcp-remote`) if you use the local-proxy option

## Use with agent

=== "Python"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters

    root_agent = Agent(
        model="gemini-flash-latest",
        name="truthifi_agent",
        instruction="Help users understand their investment accounts, fees and performance using Truthifi",
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command="npx",
                        args=["-y", "mcp-remote", "https://api.truthifi.com/mcp"],
                    ),
                    timeout=30,
                ),
            )
        ],
    )
    ```

    !!! note

        When you run this agent for the first time, a browser window opens to
        sign in to Truthifi (OAuth). No API key is needed.

=== "TypeScript"

    ```typescript
    import { LlmAgent, MCPToolset } from "@google/adk";

    const rootAgent = new LlmAgent({
        model: "gemini-flash-latest",
        name: "truthifi_agent",
        instruction: "Help users understand their investment accounts, fees and performance using Truthifi",
        tools: [
            new MCPToolset({
                type: "StdioConnectionParams",
                serverParams: {
                    command: "npx",
                    args: ["-y", "mcp-remote", "https://api.truthifi.com/mcp"],
                },
            }),
        ],
    });

    export { rootAgent };
    ```

## Available tools

Tool | Description
---- | -----------
`get_accounts` | Lists linked accounts and how far back each one's data goes
`get_dated_holdings` | Positions in each account on one day
`get_composition` | Allocation by asset class, sector, industry or country
`get_equity_concentrations` | Exposure to individual stocks, including through funds
`get_performance_history` | Return, income and gain/loss vs a similar benchmark
`get_fees` | Fees per account by type
`get_transactions` | Individual transactions, filterable and paged
`get_findings` | Financial health findings behind the Truthifi Score
`connect_account` | Returns a secure link to connect a new account

See the [full tool list](https://truthifi.com/mcp-tools) (30 tools).

## Resources

- [Truthifi MCP documentation](https://truthifi.com/mcp-tools)
- [GitHub repository](https://github.com/truthifi/truthifi-mcp)
- [Truthifi support](https://truthifi.com/help)
