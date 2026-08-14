---
catalog_title: ClickHouse Cloud
catalog_description: Query data, explore schemas, and monitor services, backups, ClickPipes, and billing in ClickHouse Cloud
catalog_icon: /integrations/assets/clickhouse.png
catalog_tags: ["database", "analytics", "mcp"]
---

# ClickHouse Cloud MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [ClickHouse Cloud remote MCP
server](https://clickhouse.com/docs/cloud/features/ai-ml/remote-mcp) connects
ADK agents directly to your ClickHouse Cloud services. Your agent can list
databases and tables, inspect schemas, run read-only SQL queries, and get
visibility into services, backups, ClickPipes, and billing, with 13 tools
available.

The server is fully hosted and requires no local installation, Docker
containers, or API key configuration. Authentication uses OAuth 2.0, and access
is scoped to the organizations and services the authenticated user has
permission to access.

## Use cases

- **Explore and analyze data**: Discover databases and tables, inspect column
  definitions, and run analytical SELECT queries in natural language. Ask
  "What's the average session duration by country for the last 7 days?" and let
  the agent translate it into SQL.
- **Generate insights and reports**: Pull analytical results into summaries,
  visualizations, or downstream workflows without building a custom data
  pipeline.
- **Monitor infrastructure**: List services in an organization, check service
  status and details, review backup schedules and recent backups, and inspect
  configured ClickPipes.
- **Track costs**: Retrieve billing and usage data for an organization,
  including daily per-entity cost records over a date range.

## Prerequisites

- A running ClickHouse instance ([ClickHouse Cloud](https://clickhouse.com/cloud)
  or self-hosted)
- **Local MCP server**: [uv](https://docs.astral.sh/uv/) installed (`uvx` is
  used to run [mcp-clickhouse](https://github.com/ClickHouse/mcp-clickhouse)),
  plus a ClickHouse user with the minimum privileges the agent needs
- **Remote MCP server** (ClickHouse Cloud only): the remote MCP server enabled
  for the service — in the ClickHouse Cloud console, open your service, click
  **Connect**, select **Connect with MCP**, and toggle it on

## Use with agent

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

        clickhouse_tools = MCPToolset(
            connection_params=StdioServerParameters(
                command="uvx",
                args=["mcp-clickhouse"],
                env={
                    "CLICKHOUSE_HOST": "<your-instance>.clickhouse.cloud",
                    "CLICKHOUSE_USER": "<clickhouse-user>",
                    "CLICKHOUSE_PASSWORD": "<clickhouse-password>",
                    "CLICKHOUSE_PORT": "8443",
                },
            )
        )

        root_agent = Agent(
            model="gemini-flash-latest",
            name="clickhouse_agent",
            instruction="Help users explore and analyze data in ClickHouse. "
            "Use the ClickHouse tools to query the data before answering. "
            "Always ground your answer in actual query results, not assumptions.",
            tools=[clickhouse_tools],
        )
        ```

        Replace `CLICKHOUSE_HOST` with your instance hostname (works with
        ClickHouse Cloud or self-hosted). Use a dedicated database user with
        only the privileges the agent needs — avoid `default` or administrative
        users. Queries run read-only by default.

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        root_agent = Agent(
            model="gemini-flash-latest",
            name="clickhouse_agent",
            instruction="Help users explore and analyze data in ClickHouse Cloud",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mcp.clickhouse.cloud/mcp",
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
            name: "clickhouse_agent",
            instruction: "Help users explore and analyze data in ClickHouse Cloud",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.clickhouse.cloud/mcp",
                }),
            ],
        });

        export { rootAgent };
        ```

!!! note

    With the remote MCP server, when the agent first connects you'll be
    prompted to authorize the connection in your browser by signing in with
    your ClickHouse Cloud credentials. Access is scoped to the organizations
    and services your user has permission to access. The local MCP server
    authenticates with the database credentials in its environment variables
    instead — no OAuth flow.

## Safety

All tools exposed by the remote MCP server are **read-only**. Each tool is
annotated with `readOnlyHint: true` in its MCP metadata. No tool can modify
data, alter service configuration, or perform any destructive operation. The
`run_select_query` tool only permits `SELECT` statements.

The local MCP server is also read-only by default. Write access requires
explicitly setting `CLICKHOUSE_ALLOW_WRITE_ACCESS=true`, and destructive
operations (DROP, TRUNCATE) additionally require `CLICKHOUSE_ALLOW_DROP=true`.

## Available tools

### Local MCP server

Tool | Description
---- | -----------
`run_query` | Execute a SQL query (read-only by default)
`list_databases` | List all databases on the ClickHouse instance
`list_tables` | List tables in a database with pagination and optional `like`/`not_like` filters

### Remote MCP server (ClickHouse Cloud)

The remote server exposes 13 read-only tools in the categories below.

### Query and schema exploration

Tool | Description
---- | -----------
`run_select_query` | Execute a read-only SELECT query against a ClickHouse service
`list_databases` | List all databases available in a ClickHouse service
`list_tables` | List all tables in a database, including column definitions, with optional `like`/`notLike` filters

### Organizations

Tool | Description
---- | -----------
`get_organizations` | Retrieve all ClickHouse Cloud organizations accessible to the authenticated user
`get_organization_details` | Return details of a single organization

### Services

Tool | Description
---- | -----------
`get_services_list` | List all services in a ClickHouse Cloud organization
`get_service_details` | Return details of a specific service

### Backups

Tool | Description
---- | -----------
`list_service_backups` | List all backups for a service, most recent first
`get_service_backup_details` | Return details of a single backup
`get_service_backup_configuration` | Return the backup configuration for a service (schedule and retention settings)

### ClickPipes

Tool | Description
---- | -----------
`list_clickpipes` | List all ClickPipes configured for a service
`get_clickpipe` | Return details of a specific ClickPipe

### Billing

Tool | Description
---- | -----------
`get_organization_cost` | Retrieve billing and usage cost data for an organization, with optional `from_date`/`to_date` (max 31-day range)

## Choosing between local and remote

|                    | Local MCP server                                                          | Remote MCP server                                                                        |
| ------------------ | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| **Source**         | [mcp-clickhouse](https://github.com/ClickHouse/mcp-clickhouse) (open source) | Fully managed by ClickHouse Cloud                                                          |
| **Transport**      | Local stdio via `uvx`                                                       | Streamable HTTP (`https://mcp.clickhouse.cloud/mcp`)                                       |
| **Works with**     | Any ClickHouse instance (self-hosted or Cloud)                              | ClickHouse Cloud services only                                                             |
| **Authentication** | Environment variables (database user)                                       | OAuth 2.0 with Cloud credentials                                                           |
| **Tools**          | 3 tools: querying and schema exploration                                    | 13 tools: querying, schema exploration, service management, backups, ClickPipes, billing |

## Additional resources

- [mcp-clickhouse on GitHub](https://github.com/ClickHouse/mcp-clickhouse)
- [ClickHouse Cloud Remote MCP Documentation](https://clickhouse.com/docs/cloud/features/ai-ml/remote-mcp)
- [Remote MCP setup guide](https://clickhouse.com/docs/products/cloud/features/ai-ml/mcp/remote-mcp)
- [ClickHouse Cloud](https://clickhouse.com/cloud)
