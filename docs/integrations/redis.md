---
catalog_title: Redis
catalog_description: Vector, hybrid, and SQL search plus session, memory, and semantic cache for agents
catalog_icon: /integrations/assets/redis.png
catalog_tags: ["data","mcp"]
---

# Redis integration for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [adk-redis integration](https://github.com/redis-developer/adk-redis)
connects your ADK agent to [Redis](https://redis.io/), giving it
RedisVL-backed search tools
over a Redis index, persistent sessions and long-term memory via
[Redis Agent Memory Server](https://github.com/redis/agent-memory-server),
and semantic caching for LLM responses and tool results. Redis runs as a
managed service or self-hosted (Redis 8.4+ with the RediSearch module).

There are four ways to use this integration:

| Approach | Description |
|----------|-------------|
| **Search tools** | Five `BaseTool` subclasses (`RedisVectorSearchTool`, `RedisHybridSearchTool`, `RedisRangeSearchTool`, `RedisTextSearchTool`, `RedisSQLSearchTool`) over RedisVL queries against a bound index. |
| **Session + Memory services** | `RedisWorkingMemorySessionService` and `RedisLongTermMemoryService` that implement ADK's `BaseSessionService` and `BaseMemoryService`, backed by Agent Memory Server. |
| **MCP toolsets** | `create_redisvl_mcp_toolset(...)` for RedisVL's MCP server (`rvl mcp`) and `create_memory_mcp_toolset(...)` for Agent Memory Server's MCP endpoint. |
| **Semantic cache** | `RedisVLCacheProvider` (self-hosted) and `LangCacheProvider` (managed via [Redis LangCache](https://redis.io/langcache)) for LLM-response and tool-result caching. |

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
- For session and memory services:
  [Redis Agent Memory Server](https://github.com/redis/agent-memory-server)
  running locally or in your environment
- For the LangCache cache provider: a
  [Redis LangCache](https://redis.io/langcache) cache and API key

## Installation

Install only the extras you need:

```bash
pip install 'adk-redis[memory]'      # session + long-term memory services
pip install 'adk-redis[search]'      # RedisVL-backed search tools
pip install 'adk-redis[sql]'         # RedisSQLSearchTool (sql-redis)
pip install 'adk-redis[mcp-search]'  # create_redisvl_mcp_toolset helper
pip install 'adk-redis[langcache]'   # managed semantic cache provider
pip install 'adk-redis[all]'         # everything above
```

## Use with agent

=== "Search tools"

    ```python
    from google.adk.agents import Agent
    from redisvl.index import SearchIndex
    from redisvl.utils.vectorize import HFTextVectorizer

    from adk_redis import RedisVectorQueryConfig, RedisVectorSearchTool

    vectorizer = HFTextVectorizer(model="sentence-transformers/all-MiniLM-L6-v2")
    index = SearchIndex.from_existing("products", redis_url="redis://localhost:6379")

    search_tool = RedisVectorSearchTool(
        index=index,
        vectorizer=vectorizer,
        config=RedisVectorQueryConfig(num_results=5),
        return_fields=["title", "price", "category"],
        name="search_products",
        description="Semantic search over the product catalog.",
    )

    root_agent = Agent(
        model="gemini-flash-latest",
        name="redis_search_agent",
        instruction="Help users find products using semantic search.",
        tools=[search_tool],
    )
    ```

=== "Sessions + Memory"

    ```python
    from google.adk.agents import Agent
    from google.adk.runners import Runner

    from adk_redis import (
        RedisLongTermMemoryService,
        RedisLongTermMemoryServiceConfig,
        RedisWorkingMemorySessionService,
        RedisWorkingMemorySessionServiceConfig,
    )

    session_service = RedisWorkingMemorySessionService(
        config=RedisWorkingMemorySessionServiceConfig(
            api_base_url="http://localhost:8000",
        ),
    )
    memory_service = RedisLongTermMemoryService(
        config=RedisLongTermMemoryServiceConfig(
            api_base_url="http://localhost:8000",
            recency_boost=True,
        ),
    )

    root_agent = Agent(
        model="gemini-flash-latest",
        name="redis_memory_agent",
        instruction="Use long-term memory to personalize responses.",
    )

    runner = Runner(
        app_name="redis_memory_app",
        agent=root_agent,
        session_service=session_service,
        memory_service=memory_service,
    )
    ```

=== "MCP toolset"

    ```python
    from google.adk.agents import Agent
    from pydantic import SecretStr

    from adk_redis import create_redisvl_mcp_toolset

    # Connect to a running `rvl mcp` server over streamable-http.
    redis_tools = create_redisvl_mcp_toolset(
        url="http://localhost:8000/mcp",
        auth_token=SecretStr("YOUR_TOKEN"),
        read_only=True,
    )

    root_agent = Agent(
        model="gemini-flash-latest",
        name="redis_mcp_agent",
        instruction="Use the search-records tool to answer questions.",
        tools=[redis_tools],
    )
    ```

=== "Semantic cache"

    ```python
    from google.adk.agents import Agent
    from redisvl.utils.vectorize import HFTextVectorizer

    from adk_redis import (
        LLMResponseCache,
        RedisVLCacheProvider,
        RedisVLCacheProviderConfig,
        create_llm_cache_callbacks,
    )

    provider = RedisVLCacheProvider(
        config=RedisVLCacheProviderConfig(
            redis_url="redis://localhost:6379",
            ttl=3600,
            distance_threshold=0.1,
        ),
        vectorizer=HFTextVectorizer(
            model="sentence-transformers/all-MiniLM-L6-v2",
        ),
    )

    llm_cache = LLMResponseCache(provider=provider)
    before_model_cb, after_model_cb = create_llm_cache_callbacks(llm_cache)

    root_agent = Agent(
        model="gemini-flash-latest",
        name="cached_agent",
        instruction="You are a helpful assistant with semantic caching enabled.",
        before_model_callback=before_model_cb,
        after_model_callback=after_model_cb,
    )
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

### MCP toolsets

Helper | Description
------ | -----------
`create_redisvl_mcp_toolset(...)` | `McpToolset` bound to a RedisVL MCP server (`rvl mcp`). Supports `stdio`, `sse`, and `streamable-http`; bearer auth on HTTP transports; `--read-only` default for stdio. Exposes `search-records` and `upsert-records`.
`create_memory_mcp_toolset(...)` | `McpToolset` bound to Agent Memory Server's MCP endpoint. Exposes `search_long_term_memory`, `create_long_term_memories`, `edit_long_term_memory`, `delete_long_term_memories`, `memory_prompt`, and related memory tools.

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
`RedisWorkingMemorySessionService` | `BaseSessionService` backed by Agent Memory Server working memory. Auto-summarizes when context window is exceeded.
`RedisLongTermMemoryService` | `BaseMemoryService` backed by Agent Memory Server long-term memory with recency-boosted semantic search.

### Cache providers

Provider | Description
-------- | -----------
`RedisVLCacheProvider` | Self-hosted semantic cache via RedisVL `SemanticCache`. Bring your own vectorizer.
`LangCacheProvider` | Managed semantic cache via [Redis LangCache](https://redis.io/langcache). Embeddings are handled server-side.

## Additional resources

- [adk-redis on GitHub](https://github.com/redis-developer/adk-redis)
- [adk-redis on PyPI](https://pypi.org/project/adk-redis/)
- [adk-redis documentation](https://redis.io/docs/latest/integrate/google-adk/)
- [Runnable examples](https://github.com/redis-developer/adk-redis/tree/main/examples)
- [Redis Agent Memory Server](https://github.com/redis/agent-memory-server)
- [RedisVL documentation](https://docs.redisvl.com)
- [Redis LangCache](https://redis.io/langcache)
