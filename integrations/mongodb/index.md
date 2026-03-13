# MongoDB MCP tool for ADK

Supported in ADKPythonTypeScript

The [MongoDB MCP Server](https://github.com/mongodb-js/mongodb-mcp-server) connects your ADK agent to [MongoDB](https://www.mongodb.com/) databases and MongoDB Atlas clusters. This integration gives your agent the ability to query collections, manage databases, and interact with MongoDB Atlas infrastructure using natural language.

## Use cases

- **Data Exploration and Analysis**: Query MongoDB collections using natural language, run aggregations, and analyze document schemas without writing complex queries manually.
- **Database Administration**: List databases and collections, create indexes, manage users, and monitor database statistics through conversational commands.
- **Atlas Infrastructure Management**: Create and manage MongoDB Atlas clusters, configure access lists, and view performance recommendations directly from your agent.

## Prerequisites

- **For database access**: A MongoDB connection string (local, self-hosted, or Atlas cluster)
- **For Atlas management**: A [MongoDB Atlas](https://www.mongodb.com/atlas) service account with API credentials (client ID and secret)

## Use with agent

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# For database access, use a connection string:
CONNECTION_STRING = "mongodb://localhost:27017/myDatabase"

# For Atlas management, use API credentials:
# ATLAS_CLIENT_ID = "YOUR_ATLAS_CLIENT_ID"
# ATLAS_CLIENT_SECRET = "YOUR_ATLAS_CLIENT_SECRET"

root_agent = Agent(
    model="gemini-2.5-pro",
    name="mongodb_agent",
    instruction="Help users query and manage MongoDB databases",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "mongodb-mcp-server",
                        "--readOnly",  # Remove for write operations
                    ],
                    env={
                        # For database access, use:
                        "MDB_MCP_CONNECTION_STRING": CONNECTION_STRING,
                        # For Atlas management, use:
                        # "MDB_MCP_API_CLIENT_ID": ATLAS_CLIENT_ID,
                        # "MDB_MCP_API_CLIENT_SECRET": ATLAS_CLIENT_SECRET,
                    },
                ),
                timeout=30,
            ),
        )
    ],
)
```

```typescript
import { LlmAgent, MCPToolset } from "@google/adk";

// For database access, use a connection string:
const CONNECTION_STRING = "mongodb://localhost:27017/myDatabase";

// For Atlas management, use API credentials:
// const ATLAS_CLIENT_ID = "YOUR_ATLAS_CLIENT_ID";
// const ATLAS_CLIENT_SECRET = "YOUR_ATLAS_CLIENT_SECRET";

const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "mongodb_agent",
    instruction: "Help users query and manage MongoDB databases",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: [
                    "-y",
                    "mongodb-mcp-server",
                    "--readOnly", // Remove for write operations
                ],
                env: {
                    // For database access, use:
                    MDB_MCP_CONNECTION_STRING: CONNECTION_STRING,
                    // For Atlas management, use:
                    // MDB_MCP_API_CLIENT_ID: ATLAS_CLIENT_ID,
                    // MDB_MCP_API_CLIENT_SECRET: ATLAS_CLIENT_SECRET,
                },
            },
        }),
    ],
});

export { rootAgent };
```

## Available tools

### MongoDB database tools

| Tool                 | Description                                     |
| -------------------- | ----------------------------------------------- |
| `find`               | Run a find query against a MongoDB collection   |
| `aggregate`          | Run an aggregation against a MongoDB collection |
| `count`              | Get the number of documents in a collection     |
| `list-databases`     | List all databases for a MongoDB connection     |
| `list-collections`   | List all collections for a given database       |
| `collection-schema`  | Describe the schema for a collection            |
| `collection-indexes` | Describe the indexes for a collection           |
| `insert-many`        | Insert documents into a collection              |
| `update-many`        | Update documents matching a filter              |
| `delete-many`        | Remove documents matching a filter              |
| `create-collection`  | Create a new collection                         |
| `drop-collection`    | Remove a collection from the database           |
| `drop-database`      | Remove a database                               |
| `create-index`       | Create an index for a collection                |
| `drop-index`         | Drop an index from a collection                 |
| `rename-collection`  | Rename a collection                             |
| `db-stats`           | Get statistics for a database                   |
| `explain`            | Get query execution statistics                  |
| `export`             | Export query results in EJSON format            |

### MongoDB Atlas tools

Note

Atlas tools require API credentials. Set `MDB_MCP_API_CLIENT_ID` and `MDB_MCP_API_CLIENT_SECRET` environment variables to enable them.

| Tool                            | Description                      |
| ------------------------------- | -------------------------------- |
| `atlas-list-orgs`               | List MongoDB Atlas organizations |
| `atlas-list-projects`           | List MongoDB Atlas projects      |
| `atlas-list-clusters`           | List MongoDB Atlas clusters      |
| `atlas-inspect-cluster`         | Inspect metadata of a cluster    |
| `atlas-list-db-users`           | List database users              |
| `atlas-create-free-cluster`     | Create a free Atlas cluster      |
| `atlas-create-project`          | Create an Atlas project          |
| `atlas-create-db-user`          | Create a database user           |
| `atlas-create-access-list`      | Configure IP access list         |
| `atlas-inspect-access-list`     | View IP access list entries      |
| `atlas-list-alerts`             | List Atlas alerts                |
| `atlas-get-performance-advisor` | Get performance recommendations  |

## Configuration

### Environment variables

| Variable                    | Description                                   |
| --------------------------- | --------------------------------------------- |
| `MDB_MCP_CONNECTION_STRING` | MongoDB connection string for database access |
| `MDB_MCP_API_CLIENT_ID`     | Atlas API client ID for Atlas tools           |
| `MDB_MCP_API_CLIENT_SECRET` | Atlas API client secret for Atlas tools       |
| `MDB_MCP_READ_ONLY`         | Enable read-only mode (`true` or `false`)     |
| `MDB_MCP_DISABLED_TOOLS`    | Comma-separated list of tools to disable      |
| `MDB_MCP_LOG_PATH`          | Directory for log files                       |

### Read-only mode

The `--readOnly` flag restricts the server to read, connect, and metadata operations only. This prevents any create, update, or delete operations, making it safe for data exploration without risk of accidental modifications.

### Disabling tools

You can disable specific tools or categories using `MDB_MCP_DISABLED_TOOLS`:

- Tool names: `find`, `aggregate`, `insert-many`, etc.
- Categories: `atlas` (all Atlas tools), `mongodb` (all database tools)
- Operation types: `create`, `update`, `delete`, `read`, `metadata`

## Additional resources

- [MongoDB MCP Server Repository](https://github.com/mongodb-js/mongodb-mcp-server)
- [MongoDB Documentation](https://www.mongodb.com/docs/)
- [MongoDB Atlas](https://www.mongodb.com/atlas)
