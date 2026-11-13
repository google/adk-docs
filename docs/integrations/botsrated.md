---
catalog_title: BotsRated
catalog_description: Check x402 sellers and MCP servers against signed probe receipts
catalog_icon: /integrations/assets/botsrated.png
catalog_tags: ["mcp"]
---

# BotsRated MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [BotsRated MCP Server](https://botsrated.com/llms.txt) connects your ADK
agent to [BotsRated](https://botsrated.com), a service that measures paid
[x402](https://www.x402.org) agent services (USDC on Base) and remote MCP
servers. BotsRated probes each covered host on a schedule without paying and
records every probe as an ed25519-signed receipt. Before your agent pays an
x402 seller, it can call the free `preflight` tool to see the latest probe:
HTTP status, whether the 402 challenge was valid, the quoted versus listed
price and pay-to address, and how fresh the data is.

## Use cases

- **Check a seller before paying**: Look up an x402 endpoint and confirm that
  its latest 402 challenge was valid and that the quoted price and pay-to
  address match its public listing.

- **Check a remote MCP server before connecting**: See the last handshake
  state (`ok`, `auth_required`, `handshake_failed`, or `unreachable`),
  protocol version, and tool count of a remote MCP server.

- **Review a host's history**: Read signed daily aggregates for a host, such as
  probe counts, latency percentiles, and the quoted amounts seen.

- **Find a provider for a task**: Get the x402 URL for a ranked list of covered
  providers that match a task, which your own x402 client can then pay for.

## Prerequisites

- No account or API key is required. The remote MCP server at
  `https://botsrated.com/mcp` accepts unauthenticated requests.
- The `preflight`, `coverage`, `sample`, and `history` tools are free. The
  `check`, `report`, and `best` tools do not make payments. They return the
  x402 URL of the matching paid endpoint (USDC on Base: $0.001, $0.002, and
  $0.01 per call). Each client IP gets 100 free check calls and 10 free report
  calls per UTC day. See [pricing](https://botsrated.com/pricing) for details.
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
`preflight` | Free. Returns the latest unpaid probe for an x402 seller or remote MCP server: status, 402 validity, quoted vs. listed price and pay-to address, freshness, and a receipt link
`coverage` | Free. Returns how many x402 hosts and remote MCP servers are covered, the discovery sources, and the probe schedule
`sample` | Free. Returns a real sample response for the paid `check`, `report`, or `best` endpoint
`history` | Free. Returns signed daily aggregates for one host (up to 90 days)
`check` | Returns the x402 URL ($0.001) for measured facts on one host, including paid test-buys with Base transaction links
`report` | Returns the x402 URL ($0.002) for the full receipt history of one host
`best` | Returns the x402 URL ($0.01) for the top 3 covered providers for a task

## Configuration

To expose only the free tools to your agent, pass a tool filter:

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
- [BotsRated repository](https://github.com/botsrated/botsrated)
- [x402 protocol](https://www.x402.org)
