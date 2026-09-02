---
catalog_title: Qdrant
catalog_description: Store and retrieve information using semantic vector search
catalog_icon: /integrations/assets/qdrant.png
catalog_tags: ["data","mcp"]
---

# Qdrant MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Qdrant MCP Server](https://github.com/qdrant/mcp-server-qdrant) connects
your ADK agent to [Qdrant](https://qdrant.tech/), an open-source vector search engine. This integration gives your agent the ability to store and
retrieve information using semantic search.

## Use cases

- **Semantic Memory for Agents**: Store conversation context, facts, or learned
  information that agents can retrieve later using natural language queries.

- **Code Repository Search**: Build a searchable index of code snippets,
  documentation, and implementation patterns that can be queried semantically.

- **Knowledge Base Retrieval**: Create a retrieval-augmented generation (RAG)
  system by storing documents and retrieving relevant context for responses.

## Prerequisites

- A running Qdrant instance. You can:
    - Use [Qdrant Cloud](https://cloud.qdrant.io/) (managed service)
    - Run locally with Docker: `docker run -p 6333:6333 qdrant/qdrant`
- (Optional) A Qdrant API key for authentication

## Use with agent

=== "Python"

    === "Local MCP Server"

        ```python
        --8<-- "examples/inline/python/integrations/qdrant/001-use-with-agent.py"
        ```

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        --8<-- "examples/inline/typescript/integrations/qdrant/002-use-with-agent.ts"
        ```

## Available tools

Tool | Description
---- | -----------
`qdrant-store` | Store information in Qdrant with optional metadata
`qdrant-find` | Search for relevant information using natural language queries

## Configuration

The Qdrant MCP server can be configured using environment variables:

Variable | Description | Default
-------- | ----------- | -------
`QDRANT_URL` | URL of the Qdrant server | `None` (required)
`QDRANT_API_KEY` | API key for Qdrant Cloud authentication | `None`
`COLLECTION_NAME` | Name of the collection to use | `None`
`QDRANT_LOCAL_PATH` | Path for local persistent storage (alternative to URL) | `None`
`EMBEDDING_MODEL` | Embedding model to use | `sentence-transformers/all-MiniLM-L6-v2`
`EMBEDDING_PROVIDER` | Provider for embeddings (`fastembed` or `ollama`) | `fastembed`
`TOOL_STORE_DESCRIPTION` | Custom description for the store tool | Default description
`TOOL_FIND_DESCRIPTION` | Custom description for the find tool | Default description

### Custom tool descriptions

You can customize the tool descriptions to guide the agent's behavior:

```python
--8<-- "examples/inline/python/integrations/qdrant/003-custom-tool-descriptions.py"
```

## Additional resources

- [Qdrant MCP Server Repository](https://github.com/qdrant/mcp-server-qdrant)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Qdrant Cloud](https://cloud.qdrant.io/)
