---
catalog_title: TrollBridge
catalog_description: Pay-per-call intel APIs for AI agents — bounties, verdicts, token safety screens, and DeFi data, tolled per call in USDC
catalog_icon: /integrations/assets/trollbridge.png
catalog_tags: ["mcp"]
---

# TrollBridge MCP for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [TrollBridge MCP Server](https://github.com/eric-tijerina/trollbridge-mcp)
connects your ADK agent to [TrollBridge](https://mini-tollbooth.onrender.com),
a pay-per-call intel bridge: 100 tolled API lanes covering bounties, verdicts,
token safety screens, wallet screening, and DeFi market data. Your agent pays
per call in USDC on Base via the x402 protocol — no signup, no API keys.

## Use cases

- **Bounty and opportunity intel**: let your agent scan live bounties, grants,
  deadlines, and sweepstakes across the agent economy.
- **Token safety screens**: check contracts, honeypots, approvals, and rug risk
  before your agent touches a token or signs anything.
- **DeFi market data**: funding rates, whale movements, DEX volumes, yields,
  and stablecoin flows, priced per call instead of per month.

## Prerequisites

- No account or API key needed.
- Tolls are pay-per-call in USDC on Base via x402. Fund a wallet with a small
  USDC balance — most lanes cost $0.02–$0.05 per call.

## Use with agent

=== "Python"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import (
        StreamableHTTPConnectionParams,
    )

    root_agent = Agent(
        model="gemini-flash-latest",
        name="trollbridge_agent",
        instruction=(
            "Use TrollBridge's pay-per-call tools for bounty intel, "
            "token safety screens, and DeFi market data."
        ),
        tools=[
            McpToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url="https://trollbridge-mcp-http.onrender.com",
                    timeout=30,
                ),
            )
        ],
    )
    ```

=== "TypeScript"

    ```typescript
    import { Agent } from '@google/adk';
    import { McpToolset } from '@google/adk/tools/mcp_tool';
    import { StreamableHTTPConnectionParams } from '@google/adk/tools/mcp_tool/mcp_session_manager';

    const rootAgent = new Agent({
      model: 'gemini-flash-latest',
      name: 'trollbridge_agent',
      instruction:
        'Use TrollBridge\u2019s pay-per-call tools for bounty intel, ' +
        'token safety screens, and DeFi market data.',
      tools: [
        new McpToolset({
          connectionParams: new StreamableHTTPConnectionParams({
            url: 'https://trollbridge-mcp-http.onrender.com',
            timeout: 30,
          }),
        }),
      ],
    });
    ```
