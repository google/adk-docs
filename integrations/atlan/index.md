# Atlan MCP tool for ADK

Supported in ADKPythonTypeScript

The [Atlan MCP Server](https://github.com/atlanhq/agent-toolkit) connects your ADK agent to [Atlan](https://www.atlan.com/), the context layer for enterprise AI, giving your agent access to your organization's context repos: the knowledge, data, and semantics your AI agents need to build effectively. This integration gives your agent the ability to search and discover enterprise context, traverse end-to-end lineage, access governed data definitions and glossaries, execute SQL, curate your metadata graph, and ensure data quality, so every agent task is grounded in trusted organizational context.

## Use cases

- **Search and discover enterprise context**: Find tables, columns, dashboards, glossary terms, and data products across your entire stack with natural language.
- **Traverse end-to-end lineage**: Trace data flow upstream and downstream across systems to understand dependencies before a schema change.
- **Access governed data definitions**: Use glossaries, data domains, and certified metadata to ground agent output in trusted organizational context.
- **Curate your metadata graph**: Update descriptions, certify assets, manage glossaries, define data quality rules and schedules, and execute SQL, all from your agent.

## Prerequisites

- An [Atlan](https://atlan.com/) tenant
- An Atlan account with permissions to access the assets you want to query
- Node.js installed locally (used by `mcp-remote` to bridge to the hosted MCP server)

## Use with agent

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters


root_agent = Agent(
    model="gemini-flash-latest",
    name="atlan_agent",
    instruction="Help users search, discover, and manage enterprise data assets using Atlan",
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

```typescript
import { LlmAgent, MCPToolset } from "@google/adk";

const rootAgent = new LlmAgent({
    model: "gemini-flash-latest",
    name: "atlan_agent",
    instruction: "Help users search, discover, and manage enterprise data assets using Atlan",
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

Note

When you run this agent for the first time, a browser window opens automatically to request access via OAuth. Alternatively, you can use the authorization URL printed in the console. You must approve this request to allow the agent to access your Atlan tenant.

## Available tools

### Discovery and search

| Tool                     | Description                                                                                                                          |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| `semantic_search_tool`   | Natural-language search across all data assets using AI-powered semantic understanding                                               |
| `search_assets_tool`     | Search assets using structured filters and conditions                                                                                |
| `traverse_lineage_tool`  | Trace data flow upstream (sources) or downstream (consumers) for an asset                                                            |
| `query_assets_tool`      | Execute SQL queries against connected data sources                                                                                   |
| `get_asset_tool`         | Get detailed information about a single asset by GUID or qualified name (including custom metadata, data quality checks, and README) |
| `resolve_metadata_tool`  | Discover metadata entities by name or description (users, classifications, custom metadata sets, glossaries, domains, data products) |
| `get_groups_tool`        | List workspace groups and their members                                                                                              |
| `search_atlan_docs_tool` | Search Atlan's product documentation and return an LLM-generated answer with source citations                                        |

### Asset updates

| Tool                          | Description                                                         |
| ----------------------------- | ------------------------------------------------------------------- |
| `update_assets_tool`          | Update asset descriptions, certificate status, README, or terms     |
| `manage_announcements_tool`   | Add or remove announcements (information, warning, issue) on assets |
| `manage_asset_lifecycle_tool` | Archive, restore, or permanently purge assets                       |

### Glossaries and domains

| Tool                         | Description                                       |
| ---------------------------- | ------------------------------------------------- |
| `create_glossaries`          | Create new glossaries                             |
| `create_glossary_terms`      | Create terms within glossaries                    |
| `create_glossary_categories` | Create categories within glossaries               |
| `create_domains`             | Create data domains and subdomains                |
| `create_data_products`       | Create data products linked to domains and assets |

### Data quality rules

| Tool                     | Description                                                                  |
| ------------------------ | ---------------------------------------------------------------------------- |
| `create_dq_rules_tool`   | Create data quality rules (null checks, uniqueness, regex, custom SQL, etc.) |
| `update_dq_rules_tool`   | Update existing data quality rules                                           |
| `schedule_dq_rules_tool` | Schedule data quality rule execution with cron expressions                   |
| `delete_dq_rules_tool`   | Delete data quality rules                                                    |

### Custom metadata

| Tool                                 | Description                                                                   |
| ------------------------------------ | ----------------------------------------------------------------------------- |
| `create_custom_metadata_set_tool`    | Create custom metadata sets with typed attributes                             |
| `add_attributes_to_cm_set_tool`      | Add new attributes to an existing custom metadata set                         |
| `remove_attributes_from_cm_set_tool` | Archive (soft-delete) attributes from a custom metadata set                   |
| `delete_custom_metadata_set_tool`    | Permanently delete a custom metadata set and clear its values from all assets |
| `update_custom_metadata_tool`        | Update custom metadata values on one or more assets                           |
| `remove_custom_metadata_tool`        | Remove a custom metadata set's values from an asset                           |

### Atlan tags

| Tool                    | Description                                 |
| ----------------------- | ------------------------------------------- |
| `add_atlan_tags_tool`   | Add Atlan tags to one or more assets        |
| `remove_atlan_tag_tool` | Remove an Atlan tag from one or more assets |

## Additional resources

- [Atlan MCP Server Repository](https://github.com/atlanhq/agent-toolkit)
- [Atlan MCP Overview](https://docs.atlan.com/product/capabilities/atlan-ai/how-tos/atlan-mcp-overview)
