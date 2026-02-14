# Pinecone MCP tool for ADK

Supported in ADKPythonTypeScript

The [Pinecone MCP Server](https://github.com/pinecone-io/pinecone-mcp) connects your ADK agent to [Pinecone](https://www.pinecone.io/), a vector database for AI applications. This integration gives your agent the ability to manage indexes, store and search data using semantic search with metadata filtering, and search across multiple indexes with reranking.

## Use cases

- **Semantic Search and Retrieval**: Search stored data using natural language queries with metadata filtering and reranking.
- **Knowledge Base Management**: Store and manage data to build and maintain retrieval-augmented generation (RAG) systems.
- **Cross-Index Search**: Search across multiple Pinecone indexes simultaneously, with automatic deduplication and reranking of results.

## Prerequisites

- A [Pinecone](https://www.pinecone.io/) account
- An API key from the [Pinecone Console](https://app.pinecone.io)

## Use with agent

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

PINECONE_API_KEY = "YOUR_PINECONE_API_KEY"

root_agent = Agent(
    model="gemini-2.5-pro",
    name="pinecone_agent",
    instruction="Help users manage and search their Pinecone vector indexes",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@pinecone-database/mcp",
                    ],
                    env={
                        "PINECONE_API_KEY": PINECONE_API_KEY,
                    }
                ),
                timeout=30,
            ),
        )
    ],
)
```

```typescript
import { LlmAgent, MCPToolset } from "@google/adk";

const PINECONE_API_KEY = "YOUR_PINECONE_API_KEY";

const rootAgent = new LlmAgent({
    model: "gemini-2.5-pro",
    name: "pinecone_agent",
    instruction: "Help users manage and search their Pinecone vector indexes",
    tools: [
        new MCPToolset({
            type: "StdioConnectionParams",
            serverParams: {
                command: "npx",
                args: ["-y", "@pinecone-database/mcp"],
                env: {
                    PINECONE_API_KEY: PINECONE_API_KEY,
                },
            },
        }),
    ],
});

export { rootAgent };
```

Note

Only indexes with [integrated inference](https://docs.pinecone.io/guides/inference/understanding-inference) are supported. Indexes without an integrated embedding model are not supported by this MCP server.

## Available tools

### Documentation

| Tool          | Description                                |
| ------------- | ------------------------------------------ |
| `search-docs` | Search the official Pinecone documentation |

### Index management

| Tool                     | Description                                                                    |
| ------------------------ | ------------------------------------------------------------------------------ |
| `list-indexes`           | List all Pinecone indexes                                                      |
| `describe-index`         | Describe the configuration of an index                                         |
| `describe-index-stats`   | Get statistics about an index, including record count and available namespaces |
| `create-index-for-model` | Create a new index with an integrated inference model for embedding            |

### Data operations

| Tool               | Description                                                                             |
| ------------------ | --------------------------------------------------------------------------------------- |
| `upsert-records`   | Insert or update records in an index with integrated inference                          |
| `search-records`   | Search for records using a text query with options for metadata filtering and reranking |
| `cascading-search` | Search across multiple indexes, deduplicating and reranking the results                 |
| `rerank-documents` | Rerank a collection of records or text documents using a specialized reranking model    |

## Additional resources

- [Pinecone MCP Server Repository](https://github.com/pinecone-io/pinecone-mcp)
- [Pinecone MCP Documentation](https://docs.pinecone.io/guides/operations/mcp-server)
- [Pinecone Documentation](https://docs.pinecone.io)
