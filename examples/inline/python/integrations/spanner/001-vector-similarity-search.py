from google.adk.agents import LlmAgent
from google.adk.tools.spanner import SpannerCredentialsConfig, SpannerToolset
from google.adk.tools.spanner.settings import (
    Capabilities,
    SpannerToolSettings,
    SpannerVectorStoreSettings,
)

# 1. Define Spanner tool config with vector store settings
my_vector_store_settings = SpannerVectorStoreSettings(
    project_id="your-gcp-project",
    instance_id="your-spanner-instance",
    database_id="your-database",
    table_name="my_products",
    content_column="productDescription",
    embedding_column="productDescriptionEmbedding",
    vector_length=768,
    vertex_ai_embedding_model_name="text-embedding-005",
    selected_columns=["productId", "productName", "productDescription"],
    nearest_neighbors_algorithm="EXACT_NEAREST_NEIGHBORS",
    top_k=3,
    distance_type="COSINE",
    additional_filter="inventoryCount > 0",
)

my_tool_settings = SpannerToolSettings(
    capabilities=[Capabilities.DATA_READ],
    vector_store_settings=my_vector_store_settings,
)

# 2. Initialize the Spanner toolset
credentials_config = SpannerCredentialsConfig()
my_spanner_toolset = SpannerToolset(
    credentials_config=credentials_config,
    spanner_tool_settings=my_tool_settings,
    tool_filter=["vector_store_similarity_search"],
)

# 3. Use the toolset in your RAG agent
my_rag_agent = LlmAgent(
    model="gemini-flash-latest",
    name="product_search_agent",
    instruction="""
    You are a helpful assistant that answers user questions by finding similar products.
    1. Always use the `vector_store_similarity_search` tool to find relevant product information.
    2. If no relevant information is found, state that no matching products were found.
    3. Present the relevant product details clearly in your response.
    """,
    tools=[my_spanner_toolset],
)