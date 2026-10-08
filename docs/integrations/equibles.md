---
catalog_title: Equibles
catalog_description: Search SEC filings and read financials, earnings calls and 13F data
catalog_icon: /integrations/assets/equibles.png
catalog_tags: ["mcp", "data"]
---

# Equibles MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Equibles MCP server](https://equibles.com/docs/mcp) connects your ADK agent
to [Equibles](https://equibles.com) US stock market data. Its tools search and
read SEC filings and earnings call transcripts, return financial statements
built from SEC XBRL data, and look up insider transactions, 13F institutional
holdings, congressional trades, short interest and daily prices. Results name
the filing or source each figure comes from.

The server is hosted at `https://mcp.equibles.com/mcp` over streamable HTTP, so
no local install is required. The agent authenticates with an API key from Equibles
sent as a Bearer token.

## Use cases

- **Research a filing**: Search 10-K, 10-Q and 8-K text across every company or
  for one ticker, then read the matching lines in full to answer questions about
  risk factors, segments or accounting policies.

- **Pull financial statements**: Fetch income statements, balance sheets and
  cash-flow statements, or one concept such as revenue or diluted EPS over time,
  to compare companies or periods.

- **Review an earnings call**: Read a speaker-labelled transcript next to the
  company's stated guidance to compare what management said with the reported
  numbers.

- **Track ownership and trading**: Check insider transactions, the largest 13F
  holders of a stock, and congressional trades reported for a ticker.

## Prerequisites

- A working [ADK installation](/get-started/installation/) with MCP support:
  `pip install "google-adk[mcp]"` for Python, or
  `npm install @google/adk @modelcontextprotocol/sdk` for TypeScript
- An API key from Equibles: create an account at [equibles.com](https://equibles.com)
  and generate a key from the dashboard, as described in
  [Authentication](https://equibles.com/docs/authentication). The key starts
  with `eq_` and is shown once.

## Use with agent

The server exposes over 100 tools. The examples below use a tool filter so the
agent only loads the tools it needs, which keeps the tool declarations sent to
the model short.

=== "Python"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

    EQUIBLES_API_KEY = "YOUR_EQUIBLES_API_KEY"

    root_agent = Agent(
        model="gemini-flash-latest",
        name="equibles_agent",
        instruction=(
            "You are a stock research assistant. Use the Equibles tools to answer "
            "questions from SEC filings, financial statements, earnings calls and "
            "ownership data, and cite the source of each figure."
        ),
        tools=[
            McpToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url="https://mcp.equibles.com/mcp",
                    headers={"Authorization": f"Bearer {EQUIBLES_API_KEY}"},
                ),
                tool_filter=[
                    "SearchDocuments",
                    "ReadDocumentLines",
                    "GetFinancialStatement",
                    "GetEarningsCallTranscript",
                    "GetInsiderTransactions",
                    "GetTopHolders",
                ],
            )
        ],
    )
    ```

=== "TypeScript"

    ```typescript
    import { LlmAgent, MCPToolset } from "@google/adk";

    const EQUIBLES_API_KEY = "YOUR_EQUIBLES_API_KEY";

    const rootAgent = new LlmAgent({
        model: "gemini-flash-latest",
        name: "equibles_agent",
        instruction:
            "You are a stock research assistant. Use the Equibles tools to answer " +
            "questions from SEC filings, financial statements, earnings calls and " +
            "ownership data, and cite the source of each figure.",
        tools: [
            new MCPToolset(
                {
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.equibles.com/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${EQUIBLES_API_KEY}`,
                            },
                        },
                    },
                },
                [
                    "SearchDocuments",
                    "ReadDocumentLines",
                    "GetFinancialStatement",
                    "GetEarningsCallTranscript",
                    "GetInsiderTransactions",
                    "GetTopHolders",
                ],
            ),
        ],
    });

    export { rootAgent };
    ```

Then ask the agent something like "Who are NVIDIA's largest institutional
holders, and as of which quarter?" or "What did Apple's latest 10-K say about
supply chain risk?".

## Available tools

The table lists commonly used tools. The
[tools reference](https://equibles.com/docs/mcp/tools) lists all of them.

Tool | Description
---- | -----------
`SearchDocuments` | Search SEC filings and earnings call transcripts across every company or for one ticker
`ReadDocumentLines` | Read numbered lines from one filing or transcript
`ListFilings` | List stored filings and transcripts for a ticker or the whole market, newest first
`GetFinancialStatement` | Get an income statement, balance sheet or cash-flow statement from SEC XBRL data
`GetFinancialFact` | Get one financial concept, such as revenue or diluted EPS, over time
`GetEarningsCallTranscript` | Get a speaker-labelled earnings call transcript for a fiscal quarter
`GetGuidance` | Get company guidance from earnings releases and earnings calls
`GetInsiderTransactions` | Get insider transactions from SEC Forms 4 and 5
`GetTopHolders` | Get the largest institutional holders of a stock from 13F filings
`GetInstitutionPortfolio` | Get an institutional investor's positions from its 13F filing
`GetCongressionalTrades` | Get securities transactions reported by members of Congress for a ticker
`GetShortInterest` | Get short interest history from FINRA
`GetStockPrices` | Get daily price history (open, high, low, close and volume)
`ScreenStocks` | Screen stocks by valuation, growth, ownership and other bounds

## Configuration

- **Tool selection**: `tool_filter` in Python, or the second `MCPToolset`
  argument in TypeScript, takes a list of tool names. Leave it out to load
  every tool.

- **Tools that write**: Most tools only read data. `CreateMyPortfolio`,
  `DeleteMyPortfolio`, `AddPortfolioLot`, `UpdatePortfolioLot`,
  `ClosePortfolioLot`, `RemovePortfolioLot`, `WatchInstrument`,
  `UnwatchInstrument`, `ReportProblem` and `SuggestToolImprovement` write to the
  Equibles account that owns the API key. Leave them out of the filter unless
  the agent should manage that account's portfolios or watchlists.

- **Usage limits**: Each tool call counts against the daily request allowance
  of the key's plan, which resets at 00:00 UTC. See
  [Rate limits](https://equibles.com/docs/rate-limits).

## Additional resources

- [Equibles MCP server documentation](https://equibles.com/docs/mcp)
- [Equibles MCP tools reference](https://equibles.com/docs/mcp/tools)
- [Equibles MCP server repository](https://github.com/daniel3303/stock-market-mcp-server)
