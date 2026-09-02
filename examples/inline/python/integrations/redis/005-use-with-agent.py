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