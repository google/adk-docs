---
catalog_title: Couchbase
catalog_description: Query collections, explore schemas, and run SQL++ queries
catalog_icon: /integrations/assets/couchbase.png
catalog_tags: ["data", "mcp"]
---

# Couchbase MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Couchbase MCP Server](https://github.com/Couchbase-Ecosystem/mcp-server-couchbase)
connects your ADK agent to [Couchbase](https://www.couchbase.com/) clusters. This
integration gives your agent the ability to explore Couchbase data using natural
language, including exploring data, running queries, and analyzing performance
issues.

## Use cases

- **Data Exploration**: Discover buckets, scopes, collections, and document
  schemas, query data using natural language queries.

- **Database Administration**: Monitor cluster health, check running services,
  and manage bucket, scope, and collection structures through conversational
  commands.

- **Query Performance Analysis**: Get index recommendations, analyze query
  plans, and investigate slow or non-selective queries to optimize performance.

## Prerequisites

- A running Couchbase cluster. You can:
    - Use [Couchbase Capella](https://cloud.couchbase.com/) (managed cloud service)
    - Run Couchbase Server 7.x+ locally or self-hosted
- Connection string and credentials (username/password or client certificate
  for mTLS) for the cluster
- [`uv`](https://docs.astral.sh/uv/) package manager installed (for the `uvx`
  command)

## Use with agent

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        CB_CONNECTION_STRING = "couchbase://localhost"
        CB_USERNAME = "Administrator"
        CB_PASSWORD = "password"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="couchbase_agent",
            instruction="Help users explore and query Couchbase databases",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="uvx",
                            args=["couchbase-mcp-server"],
                            env={
                                "CB_CONNECTION_STRING": CB_CONNECTION_STRING,
                                "CB_USERNAME": CB_USERNAME,
                                "CB_PASSWORD": CB_PASSWORD,
                                "CB_MCP_READ_ONLY_MODE": "true",  # Prevents write operations
                            },
                        ),
                        timeout=60,
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const CB_CONNECTION_STRING = "couchbase://localhost";
        const CB_USERNAME = "Administrator";
        const CB_PASSWORD = "password";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "couchbase_agent",
            instruction: "Help users explore and query Couchbase databases",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "uvx",
                        args: ["couchbase-mcp-server"],
                        env: {
                            CB_CONNECTION_STRING: CB_CONNECTION_STRING,
                            CB_USERNAME: CB_USERNAME,
                            CB_PASSWORD: CB_PASSWORD,
                            CB_MCP_READ_ONLY_MODE: "true", // Prevents write operations
                        },
                    },
                })
            ],
        });

        export { rootAgent };
        ```

## Available tools

### Cluster setup and health tools

Tool | Description
---- | -----------
`get_server_configuration_status` | Get the status of the MCP server
`test_cluster_connection` | Check the cluster credentials by connecting to the cluster
`get_cluster_health_and_services` | Get cluster health status and list of all running services

### Data model and schema discovery tools

Tool | Description
---- | -----------
`get_buckets_in_cluster` | Get a list of all the buckets in the cluster
`get_scopes_in_bucket` | Get a list of all the scopes in the specified bucket
`get_collections_in_scope` | Get a list of all the collections in a specified scope and bucket
`get_scopes_and_collections_in_bucket` | Get a list of all the scopes and collections in the specified bucket
`get_schema_for_collection` | Get the structure for a collection

### Document KV operations tools

Tool | Description
---- | -----------
`get_document_by_id` | Get a document by ID from a specified scope and collection
`upsert_document_by_id` | Upsert a document by ID to a specified scope and collection. **Disabled when `CB_MCP_READ_ONLY_MODE=true`.**
`insert_document_by_id` | Insert a new document by ID (fails if document exists). **Disabled when `CB_MCP_READ_ONLY_MODE=true`.**
`replace_document_by_id` | Replace an existing document by ID (fails if document doesn't exist). **Disabled when `CB_MCP_READ_ONLY_MODE=true`.**
`delete_document_by_id` | Delete a document by ID from a specified scope and collection. **Disabled when `CB_MCP_READ_ONLY_MODE=true`.**

### Query and indexing tools

Tool | Description
---- | -----------
`run_sql_plus_plus_query` | Run a [SQL++ query](https://www.couchbase.com/sqlplusplus/) on a specified scope
`list_indexes` | List all indexes in the cluster with their definitions, with optional filtering by bucket, scope, collection and index name
`get_index_advisor_recommendations` | Get index recommendations from Couchbase Index Advisor for a given SQL++ query to optimize query performance

### Query performance analysis tools

Tool | Description
---- | -----------
`get_longest_running_queries` | Get longest running queries by average service time
`get_most_frequent_queries` | Get most frequently executed queries
`get_queries_with_largest_response_sizes` | Get queries with the largest response sizes
`get_queries_with_large_result_count` | Get queries with the largest result counts
`get_queries_using_primary_index` | Get queries that use a primary index (potential performance concern)
`get_queries_not_using_covering_index` | Get queries that don't use a covering index
`get_queries_not_selective` | Get queries that are not selective (index scans return many more documents than final result)

## Configuration

### Environment variables

Variable | Description | Default
-------- | ----------- | -------
`CB_CONNECTION_STRING` | Connection string to the Couchbase cluster | Required
`CB_USERNAME` | Username for basic authentication | Required (or client certificate for mTLS)
`CB_PASSWORD` | Password for basic authentication | Required (or client certificate for mTLS)
`CB_CLIENT_CERT_PATH` | Path to the client certificate file for mTLS authentication | None
`CB_CLIENT_KEY_PATH` | Path to the client key file for mTLS authentication | None
`CB_CA_CERT_PATH` | Path to server root certificate for TLS (not required for Capella) | None
`CB_MCP_READ_ONLY_MODE` | Prevent all data modifications (KV and query) | `true`
`CB_MCP_DISABLED_TOOLS` | Comma-separated list of tools to disable | None

### Read-only mode

The `CB_MCP_READ_ONLY_MODE` setting (enabled by default) restricts the server to
read-only operations. When enabled, KV write tools (`upsert_document_by_id`,
`insert_document_by_id`, `replace_document_by_id`, `delete_document_by_id`) are
not loaded, and SQL++ queries that modify data are blocked. This makes it safe
for data exploration without risk of accidental modifications.

### Disabling tools

You can disable specific tools using `CB_MCP_DISABLED_TOOLS`:

```python
env={
    "CB_CONNECTION_STRING": "couchbase://localhost",
    "CB_USERNAME": "Administrator",
    "CB_PASSWORD": "password",
    "CB_MCP_DISABLED_TOOLS": "get_index_advisor_recommendations,get_queries_not_selective",
}
```

## Additional resources

- [Couchbase MCP Server Repository](https://github.com/Couchbase-Ecosystem/mcp-server-couchbase)
- [Couchbase Documentation](https://docs.couchbase.com/)
- [Couchbase Capella](https://cloud.couchbase.com/)
