---
catalog_title: SoChain
catalog_description: Look up Bitcoin, Litecoin, Dogecoin and Zcash addresses, transactions and fees
catalog_icon: /integrations/assets/sochain.png
catalog_tags: ["data", "mcp"]
---

# SoChain MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [SoChain MCP server](https://sochain.com/agents) connects your ADK agent to
[SoChain](https://sochain.com), a block explorer and API for Bitcoin, Litecoin,
Dogecoin and Zcash and their testnets. Its read-only tools look up address
balances and histories, transactions, blocks, the mempool and fee rates, so
your agent can answer questions such as "What is the balance of this Dogecoin
address?" or "Has this Bitcoin transaction confirmed?".

The server is hosted at `https://sochain.com/mcp` over Streamable HTTP, so no
local install is required. An API key is optional.

## Use cases

- **Check a payment**: Find out whether a transaction has confirmed, how many
  confirmations it has, and what it paid.

- **Research an address**: Get an address's balance, transaction history and
  counterparties, and whether it was targeted by address poisoning.

- **Choose a fee**: Read the mempool and the fee rates of the next projected
  blocks before sending a transaction.

- **Summarize a block**: Report a block's transactions, reward and fees.

## Prerequisites

- A working [ADK installation](/get-started/installation/) with MCP support:
  `pip install "google-adk[mcp]"` for Python, or
  `npm install @google/adk @modelcontextprotocol/sdk` for TypeScript
- Optional: a SoChain API key. Without one, lookups work up to 2,500 a day per
  IP address. For higher limits, create a free account and key at
  [sochain.com/dashboard](https://sochain.com/dashboard) (see
  [pricing](https://sochain.com/pricing)).

## Use with agent

The agent connects to the hosted SoChain MCP server over Streamable HTTP. When
the `SOCHAIN_API_KEY` environment variable is set, the key is sent in the
`API-KEY` header; without it, the agent works keyless.

=== "Python"

    ```python
    import os

    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

    # Optional: without a key, lookups work up to a daily limit per IP address.
    SOCHAIN_API_KEY = os.environ.get("SOCHAIN_API_KEY")

    root_agent = Agent(
        model="gemini-flash-latest",
        name="sochain_agent",
        instruction=(
            "You answer questions about Bitcoin, Litecoin, Dogecoin and Zcash "
            "addresses, transactions, blocks and fees using the SoChain tools. "
            "Quote addresses and transaction IDs in full."
        ),
        tools=[
            McpToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url="https://sochain.com/mcp",
                    headers={"API-KEY": SOCHAIN_API_KEY} if SOCHAIN_API_KEY else None,
                ),
            )
        ],
    )
    ```

=== "TypeScript"

    ```typescript
    import { LlmAgent, MCPToolset } from "@google/adk";

    // Optional: without a key, lookups work up to a daily limit per IP address.
    const SOCHAIN_API_KEY = process.env.SOCHAIN_API_KEY;

    const rootAgent = new LlmAgent({
        model: "gemini-flash-latest",
        name: "sochain_agent",
        instruction:
            "You answer questions about Bitcoin, Litecoin, Dogecoin and Zcash " +
            "addresses, transactions, blocks and fees using the SoChain tools. " +
            "Quote addresses and transaction IDs in full.",
        tools: [
            new MCPToolset({
                type: "StreamableHTTPConnectionParams",
                url: "https://sochain.com/mcp",
                transportOptions: {
                    requestInit: {
                        headers: SOCHAIN_API_KEY ? { "API-KEY": SOCHAIN_API_KEY } : {},
                    },
                },
            }),
        ],
    });

    export { rootAgent };
    ```

## Available tools

Each tool takes a network: `BTC`, `LTC`, `DOGE`, `ZEC`, or a testnet
(`BTCTEST` is Bitcoin testnet4, plus `LTCTEST`, `DOGETEST` and `ZECTEST`).

Tool | Description
---- | -----------
`get_balance` | Confirmed and unconfirmed balance of an address, or its balance at a past height or time
`get_address_summary` | An address's balance, total received, and transactions sent and received
`get_transactions` | An address's transactions, newest first, with the amount each moved for it
`get_transaction_counts` | How many transactions an address has sent, received and in total
`get_unspent_outputs` | The unspent outputs an address can spend
`get_balance_history` | An address's confirmed balance by day, week or month
`get_address_rank` | Where an address stands among the largest holders
`get_address_poisoning` | Whether an address was targeted by address poisoning
`get_counterparties` | Who an address recently sent significant amounts to and received them from
`is_valid_address` | Whether a string is a valid address on the network
`get_transaction` | A transaction's confirmations, block, fee, inputs and outputs
`get_transaction_status` | Whether a transaction is pending, mined, replaced or dropped
`get_block` | A block by height or hash: time, transactions, size, reward and fees
`get_latest_blocks` | The ten newest blocks
`get_best_block_hash` | The hash of the newest block
`get_network_info` | Current height, hashrate, and the mempool with projected next blocks and fee rates
`get_chart` | A chart series such as transaction count, fees, difficulty or hashrate
`get_rich_list` | The largest holders by confirmed balance
`get_price` | The current price, or the price on a past day
`search` | Whether a string is an address, a transaction ID, a block hash or a block height

## Configuration

The SoChain MCP server accepts one optional header:

- `API-KEY`: Your SoChain API key, for higher limits than keyless use. The same
  key works with the SoChain REST API.

To give the agent only some of the tools, pass their names as `tool_filter` to
`McpToolset` in Python, for example
`tool_filter=["get_balance", "get_transaction", "get_network_info"]`, or as the
second argument of `MCPToolset` in TypeScript.

## Additional resources

- [SoChain for agents](https://sochain.com/agents)
- [SoChain API documentation](https://sochain.com/docs)
- [SoChain pricing](https://sochain.com/pricing)
- [Get a SoChain API key](https://sochain.com/dashboard)
