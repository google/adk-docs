---
catalog_title: Redis
catalog_description: Vector, hybrid, and SQL search plus session, memory, and semantic cache for agents
catalog_icon: /integrations/assets/redis.svg
catalog_tags: ["data","mcp"]
---

# Redis integration for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [adk-redis integration](https://github.com/redis-developer/adk-redis)
connects your ADK agent to [Redis](https://redis.io/), giving it
RedisVL-backed search tools
over a Redis index, persistent sessions and long-term memory, and semantic
caching for LLM responses and tool results. Sessions and memory run on either
managed [Redis Agent Memory](https://redis.io/docs/latest/integrate/google-adk/redis-agent-memory/)
(the default) or the self-hosted
[Agent Memory Server](https://github.com/redis/agent-memory-server),
selected per service with a `backend` field. Redis runs as a
managed service or self-hosted (Redis 8.4+ with the RediSearch module).

There are several ways to use this integration:

| Approach | Description |
|----------|-------------|
| **RedisVL MCP** | Connect ADK's native `McpToolset` to a running [`rvl mcp`](https://docs.redisvl.com/en/latest/user_guide/how_to_guides/mcp.html) server. Exposes `search-records` (vector / fulltext / hybrid) and `upsert-records` with schema-aware filter and return-field hints. |
| **Session + Memory services** | `RedisSessionMemoryService` and `RedisLongTermMemoryService` that implement ADK's `BaseSessionService` and `BaseMemoryService`, backed by managed Redis Agent Memory (default) or the self-hosted Agent Memory Server, selected with a `backend` field. |
| **Memory tools** | Six `BaseTool` subclasses (`SearchMemoryTool`, `CreateMemoryTool`, `GetMemoryTool`, `UpdateMemoryTool`, `DeleteMemoryTool`, `MemoryPromptTool`) that let the LLM search, create, and manage long-term memories. Work against either backend. |
| **Sessions + Memory MCP** | Connect ADK's native `McpToolset` to [Agent Memory Server](https://github.com/redis/agent-memory-server)'s MCP endpoint over SSE. Gives the agent direct tool access to `search_long_term_memory`, `create_long_term_memories`, and `memory_prompt`. Self-hosted backend only. |
| **Search tools** | Five `BaseTool` subclasses (`RedisVectorSearchTool`, `RedisHybridSearchTool`, `RedisRangeSearchTool`, `RedisTextSearchTool`, `RedisSQLSearchTool`) over RedisVL queries against a bound index. |

## Use cases

- **RAG over your data**: Run vector, hybrid, range, BM25 text, or SQL search
  against a Redis index. Hybrid search uses native `FT.HYBRID` on Redis 8.4+
  and falls back to client-side aggregation elsewhere.
- **Persistent multi-turn agents**: Slot the session and memory services into
  any ADK `Runner` to retain conversation state, auto-summarize when the
  context window fills, and promote durable facts to long-term memory.
- **Schema-aware MCP tools**: Stand up one Redis index per `rvl mcp` server
  and connect any number of agents to it over `stdio`, `sse`, or
  `streamable-http`. The MCP tool descriptions include filter and
  return-field hints derived from the index schema.
- **Latency and cost reduction**: Wrap an LLM call site with semantic caching
  so repeat or near-duplicate prompts skip the model.

## Prerequisites

- Python 3.10+
- Redis 8.4+ (or [Redis Cloud](https://redis.io/cloud/)) with the
  RediSearch module enabled
- For session and memory services, one memory backend:
    - Managed
      [Redis Agent Memory](https://redis.io/docs/latest/integrate/google-adk/redis-agent-memory/)
      (default), which provides an API base URL, API key, and store ID, or
    - Self-hosted
      [Agent Memory Server](https://github.com/redis/agent-memory-server)
      running locally or in your environment
- For the LangCache cache provider: a
  [Redis LangCache](https://redis.io/langcache) cache and API key

## Installation

Install the components you need:

```bash
pip install 'adk-redis[memory]'      # session + long-term memory services
pip install 'adk-redis[search]'      # RedisVL-backed search tools
pip install 'adk-redis[sql]'         # RedisSQLSearchTool (sql-redis)
pip install 'adk-redis[langcache]'   # managed semantic cache provider
pip install 'adk-redis[all]'         # everything above

# For the RedisVL MCP server (used with ADK's native McpToolset):
pip install 'redisvl[mcp]>=0.18.2'
```

## Use with agent

=== "RedisVL MCP server"

    Start the [RedisVL MCP server](https://docs.redisvl.com/en/latest/user_guide/how_to_guides/mcp.html) (`rvl mcp`) pointed
    at your Redis index, then connect ADK's native `McpToolset` to it. The
    example below uses the stdio transport so no separate server process is
    needed; swap in `StreamableHTTPConnectionParams` or `SseConnectionParams` to
    connect to a long-running remote server.

    ```python
    --8<-- "examples/inline/python/integrations/redis/001-use-with-agent.py"
    ```

    !!! note

        To connect to this MCP server from other ADK languages, see [MCP
        Tools](/tools-custom/mcp-tools/).

=== "Sessions + Memory"

    Plug the session and memory services into any ADK `Runner`. Both pick a
    backend with the `backend` field: `"redis-agent-memory"` (default) for
    managed [Redis Agent Memory](https://redis.io/docs/latest/integrate/google-adk/redis-agent-memory/),
    or `"opensource-agent-memory"` for the self-hosted
    [Agent Memory Server](https://github.com/redis/agent-memory-server).
    Working memory handles per-session state; long-term memory provides
    cross-session search.

    ```python
    --8<-- "examples/inline/python/integrations/redis/002-use-with-agent.py"
    ```

    !!! note "Self-hosted backend"

        To use the self-hosted Agent Memory Server, set
        `backend="opensource-agent-memory"`, point `api_base_url` at the server
        (for example `http://localhost:8000`), and omit `api_key` and `store_id`
        unless your server requires them. Auto-summarization and recency-boosted
        search (`recency_boost=True`) are available on the self-hosted backend.

=== "Memory tools"

    Give the LLM direct control over long-term memory with the `BaseTool`
    subclasses. The agent decides when to search, create, update, or delete
    memories. The tools share a `MemoryToolConfig` and work against either
    backend via the same `backend` field.

    ```python
    --8<-- "examples/inline/python/integrations/redis/003-use-with-agent.py"
    ```

=== "Sessions + Memory MCP server"

    Connect ADK's native `McpToolset` to
    [Agent Memory Server](https://github.com/redis/agent-memory-server)'s
    MCP endpoint over SSE. This gives the agent direct tool access to
    long-term memory operations without using the REST-based services.

    ```python
    --8<-- "examples/inline/python/integrations/redis/004-use-with-agent.py"
    ```

    !!! note

        Agent Memory Server exposes its MCP endpoint on a separate port
        from the REST API. See the
        [fitness_coach_mcp example](https://github.com/redis-developer/adk-redis/tree/main/examples/fitness_coach_mcp)
        for a complete working setup with Docker Compose.

=== "Search tools"

    Use RedisVL-backed `BaseTool` subclasses to run vector, hybrid, range,
    text, or SQL searches against a Redis index. Bind a tool to an existing
    index and pass it directly to your agent.

    ```python
    --8<-- "examples/inline/python/integrations/redis/005-use-with-agent.py"
    ```

## Semantic caching

Wrap any LLM call site with semantic caching so repeat or near-duplicate
prompts skip the model. Choose self-hosted (bring your own Redis and
vectorizer) or managed via [Redis LangCache](https://redis.io/langcache).

=== "Semantic cache (self-hosted)"

    Use `RedisVLCacheProvider` with a local vectorizer and your own Redis
    instance for self-hosted semantic caching.

    ```python
    --8<-- "examples/inline/python/integrations/redis/006-semantic-caching.py"
    ```

=== "Semantic cache (LangCache)"

    Use `LangCacheProvider` with [Redis LangCache](https://redis.io/langcache),
    a managed semantic caching service. No local vectorizer is needed as
    embeddings are handled server-side.

    ```python
    --8<-- "examples/inline/python/integrations/redis/007-semantic-caching.py"
    ```

## Available tools

### Search tools

Tool | Description
---- | -----------
`RedisVectorSearchTool` | Vector similarity (KNN) search via RedisVL `VectorQuery`.
`RedisHybridSearchTool` | Vector + BM25 hybrid search. Uses native `FT.HYBRID` on Redis 8.4+; falls back to client-side aggregation otherwise.
`RedisRangeSearchTool` | Returns all documents within a vector distance threshold.
`RedisTextSearchTool` | BM25 keyword full-text search. No vectorizer required.
`RedisSQLSearchTool` | SQL `SELECT` against a bound index via `redisvl.query.SQLQuery`. Supports `:name` parameter placeholders. Requires `adk-redis[sql]`.

### MCP

Source | Description
------ | -----------
[RedisVL MCP server](https://docs.redisvl.com/en/latest/user_guide/how_to_guides/mcp.html) (`rvl mcp`) | Connect ADK's native `McpToolset` to a running `rvl mcp` server. The server exposes `search-records` (vector / fulltext / hybrid, chosen per server via YAML) and `upsert-records`, with schema-aware filter and return-field hints derived from the index. Supports `stdio`, `sse`, and `streamable-http`; bearer auth on HTTP; suppress writes with `--read-only` on the server or `tool_filter=["search-records"]` on the `McpToolset`.
[Sessions + Memory MCP server](https://github.com/redis/agent-memory-server) | Connect ADK's native `McpToolset` to Agent Memory Server's MCP endpoint over SSE. Exposes `search_long_term_memory`, `create_long_term_memories`, `edit_long_term_memory`, `delete_long_term_memories`, and `memory_prompt`. Runs on a separate port from the REST API.

### Memory tools

Tool | Description
---- | -----------
`MemoryPromptTool` | Enrich the agent prompt with relevant memories.
`SearchMemoryTool` | Search long-term memories by query.
`CreateMemoryTool` | Store new long-term memories.
`UpdateMemoryTool` | Update an existing memory by ID.
`DeleteMemoryTool` | Delete memories by ID.
`GetMemoryTool` | Fetch a single memory by ID.

### Services

Service | Description
------- | -----------
`RedisSessionMemoryService` | `BaseSessionService` backed by managed Redis Agent Memory or the self-hosted Agent Memory Server working memory. The self-hosted backend auto-summarizes when the context window is exceeded.
`RedisLongTermMemoryService` | `BaseMemoryService` backed by managed Redis Agent Memory or the self-hosted Agent Memory Server long-term memory. Recency-boosted semantic search is available on the self-hosted backend.

### Cache providers

Provider | Description
-------- | -----------
`RedisVLCacheProvider` | Self-hosted semantic cache via RedisVL `SemanticCache`. Bring your own vectorizer.
`LangCacheProvider` | Managed semantic cache via [Redis LangCache](https://redis.io/langcache). Embeddings are handled server-side.

## Additional resources

- [adk-redis on GitHub](https://github.com/redis-developer/adk-redis)
- [adk-redis on PyPI](https://pypi.org/project/adk-redis/)
- [adk-redis documentation](https://redis-developer.github.io/adk-redis/)
- [ADK + Redis on redis.io](https://redis.io/docs/latest/integrate/google-adk/)
- [Runnable examples](https://github.com/redis-developer/adk-redis/tree/main/examples)
- [Managed Redis Agent Memory](https://redis.io/docs/latest/integrate/google-adk/redis-agent-memory/)
- [Agent Memory Server (self-hosted)](https://github.com/redis/agent-memory-server)
- [RedisVL documentation](https://docs.redisvl.com)
- [Redis LangCache](https://redis.io/langcache)
