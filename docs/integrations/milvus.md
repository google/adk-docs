---
catalog_title: Milvus
catalog_description: Milvus-backed memory and RAG retrieval for ADK agents
catalog_icon: /integrations/assets/milvus.svg
catalog_tags: ["data"]
---

# Milvus integration for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [`adk-milvus`](https://github.com/zilliztech/adk-milvus) package connects
ADK Python agents to [Milvus](https://milvus.io/), an open-source vector
database. Use it for persistent semantic memory through `MilvusMemoryService`,
or expose a `milvus_similarity_search` retrieval tool for RAG workflows through
`MilvusToolset`.

Milvus can run locally with Milvus Lite, as a self-hosted Milvus server, or as a
managed [Zilliz Cloud](https://zilliz.com/cloud) deployment using the same
configuration fields.

## Use cases

- **Semantic memory for agents**: Persist session events in Milvus and retrieve
  relevant memories in later conversations.
- **RAG over private content**: Index documents or snippets and let the agent
  retrieve relevant context through a tool call.
- **Local-to-cloud development**: Start with Milvus Lite for local development,
  then switch to a Milvus server or Zilliz Cloud by changing the URI and token.

## Prerequisites

- Python 3.10 or later
- ADK for Python and `adk-milvus`
- An embedding function that returns one vector per input text
- One Milvus deployment:
    - Milvus Lite for local development
    - Milvus server, such as `http://localhost:19530`
    - Zilliz Cloud endpoint and token

## Installation

```bash
pip install adk-milvus
```

This installs the ADK runtime dependencies, PyMilvus, and Milvus Lite support.

## Configuration

Use `MILVUS_URI` and `MILVUS_TOKEN` for all deployment modes:

```bash
# Milvus Lite
export MILVUS_URI="./adk_milvus.db"

# Milvus server
export MILVUS_URI="http://localhost:19530"

# Zilliz Cloud
export MILVUS_URI="https://your-endpoint.api.gcp-us-west1.zillizcloud.com"
export MILVUS_TOKEN="your-token"
```

`MILVUS_TOKEN` is only needed for authenticated deployments such as Zilliz
Cloud. If you use a non-default Milvus database, set `MILVUS_DB_NAME`.

## Use with agent

=== "Memory service"

    Plug `MilvusMemoryService` into a `Runner` to persist and search
    cross-session memory.

    ```python
    --8<-- "examples/inline/python/integrations/milvus/001-use-with-agent.py"
    ```

    After a useful session, add it to memory and search it later:

    ```python
    --8<-- "examples/inline/python/integrations/milvus/002-use-with-agent.py"
    ```

=== "RAG toolset"

    Use `MilvusVectorStore` to index text, then expose it through
    `MilvusToolset`.

    ```python
    --8<-- "examples/inline/python/integrations/milvus/003-use-with-agent.py"
    ```

## Available tools and operations

### RAG toolset

Tool | Description
---- | -----------
`milvus_similarity_search` | Search indexed text in Milvus and return matching rows with content, source, metadata, and distance.

### Memory service

Method | Description
---- | -----------
`add_session_to_memory(session)` | Persist text-bearing events from an ADK session.
`search_memory(app_name, user_id, query)` | Search memories scoped to an ADK app and user.

## Notes

- `dimension` must match the embedding model output dimension.
- `MilvusMemoryService` scopes search by `app_name` and `user_id`.
- `MilvusVectorStore` creates the collection if it does not already exist and
  validates the existing schema before reuse.
- The collection consistency level and database name can be configured for
  deployments that need stronger read-after-write behavior or multiple Milvus
  databases.

## Resources

- [ADK Milvus package](https://github.com/zilliztech/adk-milvus)
- [ADK Milvus on PyPI](https://pypi.org/project/adk-milvus/)
- [Milvus documentation](https://milvus.io/docs)
- [Milvus Lite documentation](https://milvus.io/docs/milvus_lite.md)
- [Zilliz Cloud](https://zilliz.com/cloud)
