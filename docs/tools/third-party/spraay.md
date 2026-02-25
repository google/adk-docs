# Spraay

[Spraay](https://spraay.app) is a multi-chain batch payment protocol that enables
AI agents to send ETH or any ERC-20 token to up to 200+ recipients in a single
transaction, with ~80% gas savings compared to individual transfers. Spraay is
deployed across multiple chains including Base, Arbitrum, Unichain, Plasma, BOB,
and Bittensor.

Spraay provides both an **MCP server** for tool-based integration and
**community tools** via the
[adk-python-community](https://github.com/google/adk-python-community) package.

## Use Cases

- **Payroll**: Pay team members in ETH or stablecoins in one transaction
- **Airdrops**: Distribute tokens to community members efficiently
- **Bounties**: Send rewards to multiple contributors at once
- **Revenue sharing**: Split payments across stakeholders

## Integration via MCP Server

Spraay's MCP server connects to the
[Spraay x402 Gateway](https://gateway.spraay.app), providing 9 paid endpoints
for batch payments, token prices, wallet balances, swap quotes, and more. Agents
pay per call in USDC via the Coinbase x402 protocol — no API keys or accounts
needed.

### Setup

Install the Spraay MCP server:

```bash
npm install -g spraay-x402-mcp
```

Or clone from GitHub:

```bash
git clone https://github.com/plagtech/spraay-x402-mcp.git
```

### Usage with ADK

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams

root_agent = Agent(
    model="gemini-2.5-flash",
    name="payment_agent",
    instruction="""You are a payment assistant that helps users send
    batch cryptocurrency payments using Spraay. You can also check
    token prices, wallet balances, and get swap quotes on Base.""",
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_command="npx",
                server_args=["spraay-x402-mcp"],
            ),
        )
    ],
)
```

### Available MCP Tools

| Tool | Cost | Description |
|---|---|---|
| `spraay_batch_execute` | $0.01 | Batch payments (any ERC-20 + ETH) |
| `spraay_prices` | $0.002 | Live onchain token prices |
| `spraay_balances` | $0.002 | ETH + ERC-20 balances |
| `spraay_resolve` | $0.001 | ENS & Basename resolution |
| `spraay_swap_quote` | $0.002 | Uniswap V3 swap quotes |
| `spraay_chat` | $0.005 | AI chat via 200+ models |
| `spraay_models` | $0.001 | Available AI models |
| `spraay_tokens` | $0.001 | Supported token list |
| `spraay_gas` | $0.001 | Gas estimation |

## Integration via Community Tools

Spraay also provides native ADK function tools via the `google-adk-community`
package. See the
[adk-python-community contribution](https://github.com/google/adk-python-community)
for details.

```python
from google.adk.agents import Agent
from google.adk_community.tools.spraay import (
    spraay_batch_eth,
    spraay_batch_token,
)

agent = Agent(
    model="gemini-2.5-flash",
    name="payment_agent",
    tools=[spraay_batch_eth, spraay_batch_token],
)
```

## Resources

- **Website**: [spraay.app](https://spraay.app)
- **MCP Server**: [github.com/plagtech/spraay-x402-mcp](https://github.com/plagtech/spraay-x402-mcp)
- **Gateway**: [gateway.spraay.app](https://gateway.spraay.app)
- **Listed on**: [Smithery](https://smithery.ai) ·
  [MCP.so](https://mcp.so) ·
  [LobeHub](https://lobehub.com) ·
  [x402.org/ecosystem](https://x402.org/ecosystem)
