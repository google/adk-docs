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
over a Redis index, persistent sessions and long-term memory via
[Redis Agent Memory Server](https://github.com/redis/agent-memory-server),
and semantic caching for LLM responses and tool results. Redis runs as a
managed service or self-hosted (Redis 8.4+ with the RediSearch module).

There are four ways to use this integration:

| Approach | Description |
|----------|-------------|
| **RedisVL MCP** | Connect ADK's native `McpToolset` to a running [`rvl mcp`](https://docs.redisvl.com/en/latest/user_guide/how_to_guides/mcp.html) server. Exposes `search-records` (vector / fulltext / hybrid) and `upsert-records` with schema-aware filter and return-field hints. |
| **Session + Memory services** | `RedisWorkingMemorySessionService` and `RedisLongTermMemoryService` that implement ADK's `BaseSessionService` and `BaseMemoryService`, backed by Agent Memory Server. |
| **Search tools** | Five `BaseTool` subclasses (`RedisVectorSearchTool`, `RedisHybridSearchTool`, `RedisRangeSearchTool`, `RedisTextSearchTool`, `RedisSQLSearchTool`) over RedisVL queries against a bound index. |
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
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters

    root_agent = Agent(
        model="gemini-flash-latest",
        name="redis_mcp_agent",
        instruction="Use the search-records tool to answer questions.",
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command="rvl",
                        args=[
                            "mcp",
                            "--config",
                            "/path/to/mcp_config.yaml",
                            "--read-only",
                        ],
                    ),
                    timeout=30,
                ),
                tool_filter=["search-records"],
            ),
        ],
    )
    ```

    !!! note

        To connect to this MCP server from other ADK languages, see [MCP
        Tools](/tools-custom/mcp-tools/).

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

=== "Search tools"

    ```python
    from google.adk.agents import Agent
    from redisvl.index import SearchIndex
    from redisvl.utils.vectorize import HFTextVectorizer

    from adk_redis import RedisVectorQueryConfig, RedisVectorSearchTool

    vectorizer = HFTextVectorizer(model="redis/langcache-embed-v2")
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
            model="redis/langcache-embed-v2",
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

### MCP

Source | Description
------ | -----------
[RedisVL MCP server](https://docs.redisvl.com/en/latest/user_guide/how_to_guides/mcp.html) (`rvl mcp`) | Connect ADK's native `McpToolset` to a running `rvl mcp` server. The server exposes `search-records` (vector / fulltext / hybrid, chosen per server via YAML) and `upsert-records`, with schema-aware filter and return-field hints derived from the index. Supports `stdio`, `sse`, and `streamable-http`; bearer auth on HTTP; suppress writes with `--read-only` on the server or `tool_filter=["search-records"]` on the `McpToolset`.

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
