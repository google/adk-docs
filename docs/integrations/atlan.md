---
catalog_title: Atlan
catalog_description: Search, explore, and govern data assets in your Atlan catalog
catalog_icon: /integrations/assets/atlan.png
catalog_tags: ["mcp"]
---

# Atlan MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Atlan MCP Server](https://github.com/atlanhq/agent-toolkit) connects your
ADK agent to your [Atlan](https://www.atlan.com/) data catalog, giving the
agent the ability to discover, explore, govern, and manage data assets across
your warehouses, lakes, BI tools, and pipelines using natural language.

## Use cases

- **Asset Discovery**: Search across tables, columns, dashboards, and pipelines
  with semantic search to find the right data for an analysis or feature.

- **Lineage and Impact Analysis**: Trace upstream sources or downstream
  consumers of an asset to understand dependencies before a schema change.

- **Governance and Stewardship**: Update descriptions, certify assets,
  manage glossaries and data domains, and create or schedule data quality
  rules from the agent.

## Prerequisites

- An [Atlan](https://atlan.com/) tenant
- An Atlan account with permissions to access the assets you want to query
- Node.js installed locally (used by `mcp-remote` to bridge to the hosted
  MCP server)

## Use with agent

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters


        root_agent = Agent(
            model="gemini-flash-latest",
            name="atlan_agent",
            instruction="Help users search, explore, and govern data assets in Atlan",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "mcp-remote",
                                "https://mcp.atlan.com/mcp",
                            ]
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "atlan_agent",
            instruction: "Help users search, explore, and govern data assets in Atlan",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: [
                            "-y",
                            "mcp-remote",
                            "https://mcp.atlan.com/mcp",
                        ],
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

!!! note

    When you run this agent for the first time, a browser window opens
    automatically to request access via OAuth. Alternatively, you can use the
    authorization URL printed in the console. You must approve this request to
    allow the agent to access your Atlan tenant.

## Available tools

Tool | Description
---- | -----------
`semantic_search_tool` | Natural-language search across all data assets using AI-powered semantic understanding
`traverse_lineage_tool` | Trace data flow upstream (sources) or downstream (consumers) for an asset
`update_assets_tool` | Update asset descriptions, certificate status, README, terms, or custom metadata
`create_glossaries` | Create new glossaries
`create_glossary_terms` | Create terms within glossaries
`create_glossary_categories` | Create categories within glossaries
`create_domains` | Create data domains and subdomains
`create_data_products` | Create data products linked to domains and assets
`create_dq_rules_tool` | Create data quality rules (null checks, uniqueness, regex, custom SQL, etc.)
`update_dq_rules_tool` | Update existing data quality rules
`schedule_dq_rules_tool` | Schedule data quality rule execution with cron expressions
`delete_dq_rules_tool` | Delete data quality rules
`search_assets_tool` | Search assets using structured filters and conditions (enabled per tenant)
`get_assets_by_dsl_tool` | Query assets using Atlan's DSL for advanced filtering (enabled per tenant)
`query_assets_tool` | Execute SQL queries against connected data sources (enabled per tenant)

## Additional resources

- [Atlan MCP Server Repository](https://github.com/atlanhq/agent-toolkit)
- [Atlan MCP Overview](https://docs.atlan.com/product/capabilities/atlan-ai/how-tos/atlan-mcp-overview)
