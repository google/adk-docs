---
catalog_title: BotsRated
catalog_description: Check x402 sellers, MPP endpoints, and MCP servers against signed probe receipts
catalog_icon: /integrations/assets/botsrated.png
catalog_tags: ["mcp"]
---

# BotsRated MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [BotsRated MCP Server](https://botsrated.com/llms.txt) connects your ADK
agent to [BotsRated](https://botsrated.com), a service that measures paid
[x402](https://www.x402.org) agent services (Base and Solana mainnet USDC),
unpaid MPP/L402 payment challenges, and remote MCP servers. BotsRated probes
each covered host on a schedule without paying and records every probe as an
Ed25519-signed receipt. Before your agent pays an x402 seller, it can call the
free `preflight` tool to see the latest probe: HTTP status, whether the 402
challenge was valid, the quoted versus listed price and pay-to address, and how
fresh the data is.

## Use cases

- **Check a seller before paying**: Look up an x402 endpoint and confirm that
  its latest 402 challenge was valid and that the quoted price and pay-to
  address match its public listing.

- **Check a remote MCP server before connecting**: See the last handshake
  state (`ok`, `auth_required`, `handshake_failed`, or `unreachable`),
  protocol version, and tool count of a remote MCP server.

- **Review a host's history and hourly feed**: Read signed daily aggregates for
  a host, or subscribe to the free signed hourly change feed
  (`GET https://botsrated.com/v1/feed`).

- **Find a provider for a task**: Get the x402 URL for a list of covered
  providers that match a task, which your own x402 client can then pay for.

## Prerequisites

- No account or API key is required. The remote MCP server at
  `https://botsrated.com/mcp` accepts unauthenticated requests and exposes 14
  tools.
- Free tools: `preflight` (`1,000` calls/IP/UTC day, `25,000` with a key),
  `coverage`, `sample`, `history`, `start_upgrade`, and `find` (uses `1` of the
  free daily checks below).
- Paid tools do not make payments themselves; they return the x402 URL (USDC on
  Base) of the matching endpoint: `check` (`$0.01`, `5` free/IP/UTC day or `25`
  with a free email-verified key via `POST /v1/keys/free`, shared with `find`),
  `report` (`$0.002` from call 1 on MCP; at least `3` free/day over HTTP until
  the `15,000` overall daily free limit is reached), and `best` (`$0.01`, no
  free quota). Prepaid credit packs (`$10 / 1,000`, `$25 / 2,500`) are also
  available at `/credits`. See [pricing](https://botsrated.com/pricing) for
  details.
- For Python, install ADK with the MCP extra: `pip install "google-adk[mcp]"`.
  For TypeScript, install the MCP SDK peer dependency:
  `npm install @google/adk @modelcontextprotocol/sdk`.

## Use with agent

=== "Python"

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        root_agent = Agent(
            model="gemini-flash-latest",
            name="botsrated_agent",
            instruction=(
                "Before paying any x402 seller, call preflight on its URL and "
                "report the latest probe status, quoted price, and payTo."
            ),
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://botsrated.com/mcp",
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "botsrated_agent",
            instruction:
                "Before paying any x402 seller, call preflight on its URL and " +
                "report the latest probe status, quoted price, and payTo.",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://botsrated.com/mcp",
                }),
            ],
        });

        export { rootAgent };
        ```

## Available tools

Tool | Description
---- | -----------
`preflight` | Free (`1,000/IP/UTC day`). Returns the latest unpaid probe for an x402 seller, MPP endpoint, or remote MCP server: status, challenge validity, quoted vs. listed price and pay-to address, freshness, and a receipt link
`coverage` | Free. Returns current coverage counts across x402 hosts, MPP services, and remote MCP servers, discovery sources, and the probe schedule
`sample` | Free. Returns a real sample response for the paid `check`, `report`, or `best` endpoint
`history` | Free. Returns signed daily aggregates for one host (up to 90 days)
`find` | Free (`1` of the `5`/`25` daily free checks). Searches covered sellers and MCP servers matching a task need
`start_upgrade` | Free. Returns a personal card checkout link for prepaid credit packs (`$10 / 1,000` or `$25 / 2,500`)
`check` | Returns the x402 URL (`$0.01` after `5` free/IP/day or `25` with free key) for measured facts on one host, including paid Base test-buys with tx links
`report` | Returns the x402 URL (`$0.002` from call 1 on MCP; at least `3` free/day over HTTP) for the published receipt history of one host
`best` | Returns the x402 URL (`$0.01`, no free quota) for the top 3 covered providers for a task

## Configuration

To expose only the free lookup tools to your agent, pass a tool filter:

=== "Python"

    ```python
    McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url="https://botsrated.com/mcp",
        ),
        tool_filter=["preflight", "coverage", "sample", "history"],
    )
    ```

=== "TypeScript"

    ```typescript
    new MCPToolset(
        {
            type: "StreamableHTTPConnectionParams",
            url: "https://botsrated.com/mcp",
        },
        ["preflight", "coverage", "sample", "history"],
    )
    ```

## Additional resources

- [BotsRated](https://botsrated.com)
- [BotsRated API reference (llms.txt)](https://botsrated.com/llms.txt)
- [BotsRated pricing](https://botsrated.com/pricing)
- [BotsRated change feed](https://botsrated.com/v1/feed)
- [BotsRated repository](https://github.com/botsrated/botsrated)
- [x402 protocol](https://www.x402.org)
