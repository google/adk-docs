---
catalog_title: TickerLayer
catalog_description: Get quotes, price history, and market hours for stocks, forex, and crypto
catalog_icon: /integrations/assets/tickerlayer.png
catalog_tags: ["mcp", "data"]
---

# TickerLayer MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [TickerLayer MCP Server](https://tickerlayer.com/docs/mcp) connects your ADK
agent to [TickerLayer](https://tickerlayer.com/), a market data API. Your agent
can read quotes, recent trades, daily snapshots, and historical price bars for
stocks, ETFs, indices, forex, crypto, commodities, and perpetual futures, along
with government bond yields and market hours. Every tool is read-only: none of
them places orders or changes the account.

## Use cases

- **Market snapshots**: Answer questions like "how is Bitcoin doing today?"
  with the last price, previous close, and daily change for a stock, currency
  pair, or crypto asset.

- **Historical analysis**: Pull minute, hourly, or daily OHLCV bars between two
  dates to summarize trends, ranges, or returns over a period.

- **Market hours and holidays**: Check whether a market is open, when its next
  session starts, and which days it is closed before scheduling work.

- **Rates context**: Read government bond yields by country and tenor, such as
  the US 10-year, next to equity or currency moves.

## Prerequisites

- Create a [TickerLayer account](https://tickerlayer.com/signup) and copy your
  API key from the dashboard. The free plan covers crypto, forex, and US stocks;
  other asset classes need a [paid plan](https://tickerlayer.com/pricing).
- For TypeScript, install the MCP SDK next to ADK:
  `npm install @google/adk @modelcontextprotocol/sdk`

## Use with agent

=== "Python"

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

        TICKERLAYER_API_KEY = "YOUR_TICKERLAYER_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="market_data_agent",
            instruction="Answer questions about markets using TickerLayer market data",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mcp.tickerlayer.com/mcp",
                        headers={
                            "x-api-key": TICKERLAYER_API_KEY,
                        },
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const TICKERLAYER_API_KEY = "YOUR_TICKERLAYER_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "market_data_agent",
            instruction: "Answer questions about markets using TickerLayer market data",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.tickerlayer.com/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                "x-api-key": TICKERLAYER_API_KEY,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

!!! note "Symbol formats"

    Stocks use a country prefix (`US:KO`, `DE:SAP`), crypto and forex use joined
    pairs (`BTCUSD`, `EURUSD`), and indices use region codes (`US500`). The
    `list_symbols` and `search_symbols` tools return the symbols an API key can
    read, so the agent does not need to guess.

## Available tools

Tool | Description
---- | -----------
`get_snapshot` | Last trade, quote, previous close, and daily change for a symbol
`get_quote` | Latest bid and ask quote for a symbol
`get_last_trade` | Most recent trade: price, size, and timestamp
`get_previous_close` | Previous completed daily OHLCV bar
`get_history` | OHLCV bars between two UTC dates at minute, hour, or day intervals
`list_symbols` | Symbols the API key can read in an asset class, with an optional filter
`search_symbols` | Search symbols across all asset classes by ticker or name
`get_market_status` | Open, closed, pre-market, or post-market state by region
`get_market_sessions` | Session windows for a market or symbol on a date
`get_market_holidays` | Holiday closures and early closes by region
`get_bond_yield` | Latest government bond yield by country and tenor, such as `US:10Y`

## Additional resources

- [TickerLayer MCP Server documentation](https://tickerlayer.com/docs/mcp)
- [TickerLayer API documentation](https://tickerlayer.com/docs)
- [Rate limits](https://tickerlayer.com/docs/limits)
- [Pricing](https://tickerlayer.com/pricing)
