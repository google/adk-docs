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