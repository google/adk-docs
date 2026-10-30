# Redis integration for ADK

Supported in ADKPython

The [adk-redis integration](https://github.com/redis-developer/adk-redis) connects your ADK agent to [Redis](https://redis.io/), giving it RedisVL-backed search tools over a Redis index, persistent sessions and long-term memory, and semantic caching for LLM responses and tool results. Sessions and memory run on either managed [Redis Agent Memory](https://redis.io/docs/latest/integrate/google-adk/redis-agent-memory/) (the default) or the self-hosted [Agent Memory Server](https://github.com/redis/agent-memory-server), selected per service with a `backend` field. Redis runs as a managed service or self-hosted (Redis 8.4+ with the RediSearch module).

There are several ways to use this integration:

| Approach                      | Description                                                                                                                                                                                                                                                                    |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **RedisVL MCP**               | Connect ADK's native `McpToolset` to a running [`rvl mcp`](https://docs.redisvl.com/en/latest/user_guide/how_to_guides/mcp.html) server. Exposes `search-records` (vector / fulltext / hybrid) and `upsert-records` with schema-aware filter and return-field hints.           |
| **Session + Memory services** | `RedisSessionMemoryService` and `RedisLongTermMemoryService` that implement ADK's `BaseSessionService` and `BaseMemoryService`, backed by managed Redis Agent Memory (default) or the self-hosted Agent Memory Server, selected with a `backend` field.                        |
| **Memory tools**              | Six `BaseTool` subclasses (`SearchMemoryTool`, `CreateMemoryTool`, `GetMemoryTool`, `UpdateMemoryTool`, `DeleteMemoryTool`, `MemoryPromptTool`) that let the LLM search, create, and manage long-term memories. Work against either backend.                                   |
| **Sessions + Memory MCP**     | Connect ADK's native `McpToolset` to [Agent Memory Server](https://github.com/redis/agent-memory-server)'s MCP endpoint over SSE. Gives the agent direct tool access to `search_long_term_memory`, `create_long_term_memories`, and `memory_prompt`. Self-hosted backend only. |
| **Search tools**              | Five `BaseTool` subclasses (`RedisVectorSearchTool`, `RedisHybridSearchTool`, `RedisRangeSearchTool`, `RedisTextSearchTool`, `RedisSQLSearchTool`) over RedisVL queries against a bound index.                                                                                 |

## Use cases

- **RAG over your data**: Run vector, hybrid, range, BM25 text, or SQL search against a Redis index. Hybrid search uses native `FT.HYBRID` on Redis 8.4+ and falls back to client-side aggregation elsewhere.
- **Persistent multi-turn agents**: Slot the session and memory services into any ADK `Runner` to retain conversation state, auto-summarize when the context window fills, and promote durable facts to long-term memory.
- **Schema-aware MCP tools**: Stand up one Redis index per `rvl mcp` server and connect any number of agents to it over `stdio`, `sse`, or `streamable-http`. The MCP tool descriptions include filter and return-field hints derived from the index schema.
- **Latency and cost reduction**: Wrap an LLM call site with semantic caching so repeat or near-duplicate prompts skip the model.

## Prerequisites

- Python 3.10+
- Redis 8.4+ (or [Redis Cloud](https://redis.io/cloud/)) with the RediSearch module enabled
- For session and memory services, one memory backend:
  - Managed [Redis Agent Memory](https://redis.io/docs/latest/integrate/google-adk/redis-agent-memory/) (default), which provides an API base URL, API key, and store ID, or
  - Self-hosted [Agent Memory Server](https://github.com/redis/agent-memory-server) running locally or in your environment
- For the LangCache cache provider: a [Redis LangCache](https://redis.io/langcache) cache and API key

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

Start the [RedisVL MCP server](https://docs.redisvl.com/en/latest/user_guide/how_to_guides/mcp.html) (`rvl mcp`) pointed at your Redis index, then connect ADK's native `McpToolset` to it. The example below uses the stdio transport so no separate server process is needed; swap in `StreamableHTTPConnectionParams` or `SseConnectionParams` to connect to a long-running remote server.

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

Note

To connect to this MCP server from other ADK languages, see [MCP Tools](/tools-custom/mcp-tools/).

Plug the session and memory services into any ADK `Runner`. Both pick a backend with the `backend` field: `"redis-agent-memory"` (default) for managed [Redis Agent Memory](https://redis.io/docs/latest/integrate/google-adk/redis-agent-memory/), or `"opensource-agent-memory"` for the self-hosted [Agent Memory Server](https://github.com/redis/agent-memory-server). Working memory handles per-session state; long-term memory provides cross-session search.

```python
from google.adk.agents import Agent
from google.adk.runners import Runner

from adk_redis import (
    RedisLongTermMemoryService,
    RedisLongTermMemoryServiceConfig,
    RedisSessionMemoryService,
    RedisSessionMemoryServiceConfig,
)

# Managed Redis Agent Memory (the default backend).
session_service = RedisSessionMemoryService(
    config=RedisSessionMemoryServiceConfig(
        backend="redis-agent-memory",
        api_base_url="https://your-endpoint.redis.io",
        api_key="...",
        store_id="...",
        default_namespace="my_app",
    ),
)
memory_service = RedisLongTermMemoryService(
    config=RedisLongTermMemoryServiceConfig(
        backend="redis-agent-memory",
        api_base_url="https://your-endpoint.redis.io",
        api_key="...",
        store_id="...",
        default_namespace="my_app",
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

Self-hosted backend

To use the self-hosted Agent Memory Server, set `backend="opensource-agent-memory"`, point `api_base_url` at the server (for example `http://localhost:8000`), and omit `api_key` and `store_id` unless your server requires them. Auto-summarization and recency-boosted search (`recency_boost=True`) are available on the self-hosted backend.

Give the LLM direct control over long-term memory with the `BaseTool` subclasses. The agent decides when to search, create, update, or delete memories. The tools share a `MemoryToolConfig` and work against either backend via the same `backend` field.

```python
from google.adk.agents import Agent

from adk_redis import (
    CreateMemoryTool,
    DeleteMemoryTool,
    MemoryPromptTool,
    MemoryToolConfig,
    SearchMemoryTool,
    UpdateMemoryTool,
)

config = MemoryToolConfig(
    backend="redis-agent-memory",
    api_base_url="https://your-endpoint.redis.io",
    api_key="...",
    store_id="...",
    default_namespace="my_app",
)

root_agent = Agent(
    model="gemini-flash-latest",
    name="redis_memory_tools_agent",
    instruction="Search memory before answering. Store important facts.",
    tools=[
        SearchMemoryTool(config=config),
        CreateMemoryTool(config=config),
        UpdateMemoryTool(config=config),
        DeleteMemoryTool(config=config),
        MemoryPromptTool(config=config),
    ],
)
```

Connect ADK's native `McpToolset` to [Agent Memory Server](https://github.com/redis/agent-memory-server)'s MCP endpoint over SSE. This gives the agent direct tool access to long-term memory operations without using the REST-based services.

```python
import os

from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

MEMORY_MCP_URL = os.getenv("MEMORY_MCP_URL", "http://localhost:9000")

root_agent = Agent(
    model="gemini-flash-latest",
    name="memory_mcp_agent",
    instruction="Use memory tools to personalize responses.",
    tools=[
        McpToolset(
            connection_params=SseConnectionParams(
                url=f"{MEMORY_MCP_URL.rstrip('/')}/sse",
            ),
            tool_filter=[
                "search_long_term_memory",
                "create_long_term_memories",
                "memory_prompt",
            ],
        ),
    ],
)
```

Note

Agent Memory Server exposes its MCP endpoint on a separate port from the REST API. See the [fitness_coach_mcp example](https://github.com/redis-developer/adk-redis/tree/main/examples/fitness_coach_mcp) for a complete working setup with Docker Compose.

Use RedisVL-backed `BaseTool` subclasses to run vector, hybrid, range, text, or SQL searches against a Redis index. Bind a tool to an existing index and pass it directly to your agent.

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

## Semantic caching

Wrap any LLM call site with semantic caching so repeat or near-duplicate prompts skip the model. Choose self-hosted (bring your own Redis and vectorizer) or managed via [Redis LangCache](https://redis.io/langcache).

Use `RedisVLCacheProvider` with a local vectorizer and your own Redis instance for self-hosted semantic caching.

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

Use `LangCacheProvider` with [Redis LangCache](https://redis.io/langcache), a managed semantic caching service. No local vectorizer is needed as embeddings are handled server-side.

```python
import os

from google.adk.agents import Agent

from adk_redis import (
    LLMResponseCache,
    LangCacheProvider,
    LangCacheProviderConfig,
    create_llm_cache_callbacks,
)

provider = LangCacheProvider(
    config=LangCacheProviderConfig(
        cache_id=os.environ["LANGCACHE_CACHE_ID"],
        api_key=os.environ["LANGCACHE_API_KEY"],
        server_url=os.getenv(
            "LANGCACHE_SERVER_URL",
            "https://aws-us-east-1.langcache.redis.io",
        ),
        ttl=3600,
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

| Tool                    | Description                                                                                                                          |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `RedisVectorSearchTool` | Vector similarity (KNN) search via RedisVL `VectorQuery`.                                                                            |
| `RedisHybridSearchTool` | Vector + BM25 hybrid search. Uses native `FT.HYBRID` on Redis 8.4+; falls back to client-side aggregation otherwise.                 |
| `RedisRangeSearchTool`  | Returns all documents within a vector distance threshold.                                                                            |
| `RedisTextSearchTool`   | BM25 keyword full-text search. No vectorizer required.                                                                               |
| `RedisSQLSearchTool`    | SQL `SELECT` against a bound index via `redisvl.query.SQLQuery`. Supports `:name` parameter placeholders. Requires `adk-redis[sql]`. |

### MCP

| Source                                                                                                 | Description                                                                                                                                                                                                                                                                                                                                                                                                                                |
| ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [RedisVL MCP server](https://docs.redisvl.com/en/latest/user_guide/how_to_guides/mcp.html) (`rvl mcp`) | Connect ADK's native `McpToolset` to a running `rvl mcp` server. The server exposes `search-records` (vector / fulltext / hybrid, chosen per server via YAML) and `upsert-records`, with schema-aware filter and return-field hints derived from the index. Supports `stdio`, `sse`, and `streamable-http`; bearer auth on HTTP; suppress writes with `--read-only` on the server or `tool_filter=["search-records"]` on the `McpToolset`. |
| [Sessions + Memory MCP server](https://github.com/redis/agent-memory-server)                           | Connect ADK's native `McpToolset` to Agent Memory Server's MCP endpoint over SSE. Exposes `search_long_term_memory`, `create_long_term_memories`, `edit_long_term_memory`, `delete_long_term_memories`, and `memory_prompt`. Runs on a separate port from the REST API.                                                                                                                                                                    |

### Memory tools

| Tool               | Description                                     |
| ------------------ | ----------------------------------------------- |
| `MemoryPromptTool` | Enrich the agent prompt with relevant memories. |
| `SearchMemoryTool` | Search long-term memories by query.             |
| `CreateMemoryTool` | Store new long-term memories.                   |
| `UpdateMemoryTool` | Update an existing memory by ID.                |
| `DeleteMemoryTool` | Delete memories by ID.                          |
| `GetMemoryTool`    | Fetch a single memory by ID.                    |

### Services

| Service                      | Description                                                                                                                                                                                   |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `RedisSessionMemoryService`  | `BaseSessionService` backed by managed Redis Agent Memory or the self-hosted Agent Memory Server working memory. The self-hosted backend auto-summarizes when the context window is exceeded. |
| `RedisLongTermMemoryService` | `BaseMemoryService` backed by managed Redis Agent Memory or the self-hosted Agent Memory Server long-term memory. Recency-boosted semantic search is available on the self-hosted backend.    |

### Cache providers

| Provider               | Description                                                                                                   |
| ---------------------- | ------------------------------------------------------------------------------------------------------------- |
| `RedisVLCacheProvider` | Self-hosted semantic cache via RedisVL `SemanticCache`. Bring your own vectorizer.                            |
| `LangCacheProvider`    | Managed semantic cache via [Redis LangCache](https://redis.io/langcache). Embeddings are handled server-side. |

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
