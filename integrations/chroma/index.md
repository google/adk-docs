# Chroma MCP tool for ADK

Supported in ADKPythonTypeScript

The [Chroma MCP Server](https://github.com/chroma-core/chroma-mcp) connects your ADK agent to [Chroma](https://www.trychroma.com/), an open-source embedding database. This integration gives your agent the ability to create collections, store documents, and retrieve information using semantic search, full text search, and metadata filtering.

## Use cases

- **Semantic Memory for Agents**: Store conversation context, facts, or learned information that agents can retrieve later using natural language queries.
- **Knowledge Base Retrieval**: Build a retrieval-augmented generation (RAG) system by storing documents and retrieving relevant context for responses.
- **Persistent Context Across Sessions**: Maintain long-term memory across conversations, allowing agents to reference past interactions and accumulated knowledge.

## Prerequisites

- **For local storage**: A directory path to persist data
- **For Chroma Cloud**: A [Chroma Cloud](https://www.trychroma.com/) account with tenant ID, database name, and API key

## Use with agent

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# For local storage, use:
DATA_DIR = "/path/to/your/data/directory"

# For Chroma Cloud, use:
# CHROMA_TENANT = "your-tenant-id"
# CHROMA_DATABASE = "your-database-name"
# CHROMA_API_KEY = "your-api-key"

root_agent = Agent(
    model="gemini-2.5-pro",
    name="chroma_agent",
    instruction="Help users store and retrieve information using semantic search",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="uvx",
                    args=[
                        "chroma-mcp",
                        # For local storage, use:
                        "--client-type",
                        "persistent",
                        "--data-dir",
                        DATA_DIR,
                        # For Chroma Cloud, use:
                        # "--client-type",
                        # "cloud",
                        # "--tenant",
                        # CHROMA_TENANT,
                        # "--database",
                        # CHROMA_DATABASE,
                        # "--api-key",
                        # CHROMA_API_KEY,
                    ],
                ),
                timeout=30,
            ),
        )
    ],
)
```

```typescript
import { LlmAgent, MCPToolset } from "@google/adk";

// For local storage, use:
const DATA_DIR = "/path/to/your/data/directory";

// For Chroma Cloud, use:
// const CHROMA_TENANT = "your-tenant-id";
// const CHROMA_DATABASE = "your-database-name";
// const CHROMA_API_KEY = "your-api-key";

const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "chroma_agent",
    instruction: "Help users store and retrieve information using semantic search",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "uvx",
                args: [
                    "chroma-mcp",
                    // For local storage, use:
                    "--client-type",
                    "persistent",
                    "--data-dir",
                    DATA_DIR,
                    // For Chroma Cloud, use:
                    // "--client-type",
                    // "cloud",
                    // "--tenant",
                    // CHROMA_TENANT,
                    // "--database",
                    // CHROMA_DATABASE,
                    // "--api-key",
                    // CHROMA_API_KEY,
                ],
            },
        }),
    ],
});

export { rootAgent };
```

## Available tools

### Collection management

| Tool                          | Description                                              |
| ----------------------------- | -------------------------------------------------------- |
| `chroma_list_collections`     | List all collections with pagination support             |
| `chroma_create_collection`    | Create a new collection with optional HNSW configuration |
| `chroma_get_collection_info`  | Get detailed information about a collection              |
| `chroma_get_collection_count` | Get the number of documents in a collection              |
| `chroma_modify_collection`    | Update a collection's name or metadata                   |
| `chroma_delete_collection`    | Delete a collection                                      |
| `chroma_peek_collection`      | View a sample of documents in a collection               |

### Document operations

| Tool                      | Description                                                   |
| ------------------------- | ------------------------------------------------------------- |
| `chroma_add_documents`    | Add documents with optional metadata and custom IDs           |
| `chroma_query_documents`  | Query documents using semantic search with advanced filtering |
| `chroma_get_documents`    | Retrieve documents by IDs or filters with pagination          |
| `chroma_update_documents` | Update existing documents' content, metadata, or embeddings   |
| `chroma_delete_documents` | Delete specific documents from a collection                   |

## Configuration

The Chroma MCP server supports multiple client types to suit different needs:

### Client types

| Client Type  | Description                                                | Key Arguments                                            |
| ------------ | ---------------------------------------------------------- | -------------------------------------------------------- |
| `ephemeral`  | In-memory storage, cleared on restart. Useful for testing. | None (default)                                           |
| `persistent` | File-based storage on your local machine                   | `--data-dir`                                             |
| `http`       | Connect to a self-hosted Chroma server                     | `--host`, `--port`, `--ssl`, `--custom-auth-credentials` |
| `cloud`      | Connect to Chroma Cloud (api.trychroma.com)                | `--tenant`, `--database`, `--api-key`                    |

### Environment variables

You can also configure the client using environment variables. Command-line arguments take precedence over environment variables.

| Variable             | Description                                                |
| -------------------- | ---------------------------------------------------------- |
| `CHROMA_CLIENT_TYPE` | Client type: `ephemeral`, `persistent`, `http`, or `cloud` |
| `CHROMA_DATA_DIR`    | Path for persistent local storage                          |
| `CHROMA_TENANT`      | Tenant ID for Chroma Cloud                                 |
| `CHROMA_DATABASE`    | Database name for Chroma Cloud                             |
| `CHROMA_API_KEY`     | API key for Chroma Cloud                                   |
| `CHROMA_HOST`        | Host for self-hosted HTTP client                           |
| `CHROMA_PORT`        | Port for self-hosted HTTP client                           |
| `CHROMA_SSL`         | Enable SSL for HTTP client (`true` or `false`)             |
| `CHROMA_DOTENV_PATH` | Path to `.env` file (defaults to `.chroma_env`)            |

## Additional resources

- [Chroma MCP Server Repository](https://github.com/chroma-core/chroma-mcp)
- [Chroma Documentation](https://docs.trychroma.com/)
- [Chroma Cloud](https://www.trychroma.com/)
