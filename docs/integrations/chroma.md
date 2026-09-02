---
catalog_title: Chroma
catalog_description: Store and retrieve information using semantic vector search
catalog_icon: /integrations/assets/chroma.png
catalog_tags: ["data","mcp"]
---

# Chroma MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Chroma MCP Server](https://github.com/chroma-core/chroma-mcp) connects your
ADK agent to [Chroma](https://www.trychroma.com/), an open-source embedding
database. This integration gives your agent the ability to create collections,
store documents, and retrieve information using semantic search, full text
search, and metadata filtering.

## Use cases

- **Semantic Memory for Agents**: Store conversation context, facts, or learned
  information that agents can retrieve later using natural language queries.

- **Knowledge Base Retrieval**: Build a retrieval-augmented generation (RAG)
  system by storing documents and retrieving relevant context for responses.

- **Persistent Context Across Sessions**: Maintain long-term memory across
  conversations, allowing agents to reference past interactions and accumulated
  knowledge.

## Prerequisites

- **For local storage**: A directory path to persist data
- **For Chroma Cloud**: A [Chroma Cloud](https://www.trychroma.com/) account
  with tenant ID, database name, and API key

## Use with agent

=== "Python"

    === "Local MCP Server"

        ```python
        --8<-- "examples/inline/python/integrations/chroma/001-use-with-agent.py"
        ```

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        --8<-- "examples/inline/typescript/integrations/chroma/002-use-with-agent.ts"
        ```

## Available tools

### Collection management

Tool | Description
---- | -----------
`chroma_list_collections` | List all collections with pagination support
`chroma_create_collection` | Create a new collection with optional HNSW configuration
`chroma_get_collection_info` | Get detailed information about a collection
`chroma_get_collection_count` | Get the number of documents in a collection
`chroma_modify_collection` | Update a collection's name or metadata
`chroma_delete_collection` | Delete a collection
`chroma_peek_collection` | View a sample of documents in a collection

### Document operations

Tool | Description
---- | -----------
`chroma_add_documents` | Add documents with optional metadata and custom IDs
`chroma_query_documents` | Query documents using semantic search with advanced filtering
`chroma_get_documents` | Retrieve documents by IDs or filters with pagination
`chroma_update_documents` | Update existing documents' content, metadata, or embeddings
`chroma_delete_documents` | Delete specific documents from a collection

## Configuration

The Chroma MCP server supports multiple client types to suit different needs:

### Client types

Client Type | Description | Key Arguments
----------- | ----------- | -------------
`ephemeral` | In-memory storage, cleared on restart. Useful for testing. | None (default)
`persistent` | File-based storage on your local machine | `--data-dir`
`http` | Connect to a self-hosted Chroma server | `--host`, `--port`, `--ssl`, `--custom-auth-credentials`
`cloud` | Connect to Chroma Cloud (api.trychroma.com) | `--tenant`, `--database`, `--api-key`

### Environment variables

You can also configure the client using environment variables. Command-line
arguments take precedence over environment variables.

Variable | Description
-------- | -----------
`CHROMA_CLIENT_TYPE` | Client type: `ephemeral`, `persistent`, `http`, or `cloud`
`CHROMA_DATA_DIR` | Path for persistent local storage
`CHROMA_TENANT` | Tenant ID for Chroma Cloud
`CHROMA_DATABASE` | Database name for Chroma Cloud
`CHROMA_API_KEY` | API key for Chroma Cloud
`CHROMA_HOST` | Host for self-hosted HTTP client
`CHROMA_PORT` | Port for self-hosted HTTP client
`CHROMA_SSL` | Enable SSL for HTTP client (`true` or `false`)
`CHROMA_DOTENV_PATH` | Path to `.env` file (defaults to `.chroma_env`)

## Additional resources

- [Chroma MCP Server Repository](https://github.com/chroma-core/chroma-mcp)
- [Chroma Documentation](https://docs.trychroma.com/)
- [Chroma Cloud](https://www.trychroma.com/)
