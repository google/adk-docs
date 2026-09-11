---
catalog_title: Agent Guild
catalog_description: Check agent endpoints and inspect pricing before delegation
catalog_icon: /integrations/assets/agent-guild.svg
catalog_tags: ["mcp"]
---

# Agent Guild MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Agent Guild](https://github.com/AgentTanuki/agent-guild) provides endpoint
preflight, signed reputation evidence, and pricing discovery through a hosted
MCP server. Connect it with ADK's MCP toolset to inspect an external agent before
deciding whether to delegate work to it.

## Use cases

- **Inspect a delegation target**: Compare an endpoint's advertised capabilities
  with the observations and unknowns returned by a live preflight.
- **Check costs before use**: Retrieve current paid-operation prices, callable
  entrypoints, and free alternatives before choosing a trust operation.
- **Review evidence limits**: Keep unavailable checks and uncertainty visible
  when explaining whether an endpoint is suitable for a task.

## Prerequisites

- Set up ADK and model access using the [Python](/get-started/python/) or
  [TypeScript](/get-started/typescript/) quickstart.
- Install MCP support for the language you use:

    === "Python"

        ```bash
        pip install "google-adk[mcp]"
        ```

    === "TypeScript"

        ```bash
        npm install @google/adk "@modelcontextprotocol/sdk@^1.26.0"
        ```

The two tools in this example are free and require no Agent Guild account,
API key, or wallet. Model-provider usage follows your model provider's pricing.
Preflight sends the selected public endpoint URL to Agent Guild's hosted service,
which probes that endpoint. Supply public URLs without embedded credentials.

## Use with agent

The tool filter exposes only endpoint preflight and pricing discovery. It does
not expose registration, payment, or paid trust-read tools to the agent.

=== "Python"

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        root_agent = Agent(
            model="gemini-flash-latest",
            name="agent_guild_preflight",
            instruction=(
                "Inspect the public agent endpoint the user supplies before delegation. "
                "Use guild_preflight and report its observations and unknowns. "
                "Use guild_paid_operations when the user asks about trust-operation prices. "
                "A preflight result is evidence, not a guarantee or permission to execute."
            ),
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://agent-guild-5d5r.onrender.com/mcp",
                        timeout=30,
                    ),
                    tool_filter=["guild_preflight", "guild_paid_operations"],
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
            name: "agent_guild_preflight",
            instruction:
                "Inspect the public agent endpoint the user supplies before delegation. " +
                "Use guild_preflight and report its observations and unknowns. " +
                "Use guild_paid_operations when the user asks about trust-operation prices. " +
                "A preflight result is evidence, not a guarantee or permission to execute.",
            tools: [
                new MCPToolset(
                    {
                        type: "StreamableHTTPConnectionParams",
                        url: "https://agent-guild-5d5r.onrender.com/mcp",
                    },
                    ["guild_preflight", "guild_paid_operations"],
                ),
            ],
        });

        export { rootAgent };
        ```

Run the agent using the quickstart for your language. For example, ask it to
inspect a public agent endpoint you operate and explain which checks were
inconclusive. Then ask which paid trust operations are available and what each
currently costs.

## Available tools

Tool | Description
---- | -----------
`guild_preflight` | Probe a public agent endpoint and return observed capabilities, evidence, and unknowns. Free without a key.
`guild_paid_operations` | List current paid-operation prices, entrypoints, settlement resources, and free alternatives. This discovery call is free.

The server also offers signed Agent Passports and paid trust reads. These are
outside this example's tool filter. A signature establishes origin and
integrity, not the safety of an agent's messages or the quality of future work.
Paid reads such as `guild_check` require the current payment terms or funded
sandbox credits; do not treat them as free preflight calls.

## Additional resources

- [Agent Guild repository and API documentation](https://github.com/AgentTanuki/agent-guild)
- [Agent Guild machine-readable service guide](https://agent-guild-5d5r.onrender.com/llms.txt)
- [MCP tools in ADK](/tools-custom/mcp-tools/)
