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