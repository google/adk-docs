---
catalog_title: Spanner Tools
catalog_description: Interact with Spanner to retrieve data, search, and execute SQL
catalog_icon: /integrations/assets/spanner.png
catalog_tags: ["data","google"]
---

# Google Cloud Spanner tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.11.0</span>
</div>

These are a set of tools aimed to provide integration with Spanner, namely:

* **`list_table_names`**: Fetches table names present in a GCP Spanner database.
* **`list_table_indexes`**: Fetches table indexes present in a GCP Spanner database.
* **`list_table_index_columns`**: Fetches table index columns present in a GCP Spanner database.
* **`list_named_schemas`**: Fetches named schema for a Spanner database.
* **`get_table_schema`**: Fetches Spanner database table schema and metadata information.
* **`execute_sql`**: Runs a SQL query in Spanner database and fetch the result.
* **`similarity_search`**: Similarity search in Spanner using a text query.

They are packaged in the toolset `SpannerToolset`.

```py
--8<-- "examples/python/snippets/tools/built-in-tools/spanner.py"
```

## Perform vector similarity search

The `vector_store_similarity_search` tool enables agents to perform semantic searches against a Spanner table configured as a vector store. 
This capability is essential for building contextually aware RAG applications.

### Configure the parameters

The `SpannerVectorStoreSettings` configuration class defines the parameters for how `vector_store_similarity_search` operates. Use the following parameters:

**Required parameters**

* **`project_id`**: Your Google Cloud Project ID required for authentication context.
* **`instance_id`**: The Spanner instance ID
* **`database_id`**: The Spanner database ID.
* **`table_name`**: The Spanner table containing the vector embeddings.
* **`embedding_column`**: The `ARRAY<FLOAT>` or `ARRAY<DOUBLE>` column where the vector embeddings are stored.
* **`content_column`**: The column containing the original text or content to be retrieved.
* **`vector_length`**: The dimensionality of your embedding vectors that must match your model.
* **`vertex_ai_embedding_model_name`**: The Vertex AI model used to generate the embeddings, for example "text-embedding-005").

**Optional parameters**

* **`selected_columns`**: A list of columns you can include in the search results, such as metadata or identifiers.
* **`nearest_neighbors_algorithm`**: The algorithm you use for the search, such as "EXACT_NEAREST_NEIGHBORS".
* **`top_k`**: The number of nearest neighbors to retrieve per query.
* **`distance_type`**: The distance metric used for similarity calculation, such as "COSINE" or "EUCLIDEAN".
* **`additional_filter`**: An optional SQL filter string to apply during the search, for example: "inventoryCount > 0".
  
```py
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.spanner.settings import Capabilities, SpannerToolSettings, SpannerVectorStoreSettings, SpannerCredentialsConfig
from google.adk.tools.spanner.spanner_toolset import SpannerToolset

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
    model="gemini-2.5-flash",
    name="product_search_agent",
    instruction="""
    You are a helpful assistant that answers user questions by finding similar products.
    1. Always use the `vector_store_similarity_search` tool to find relevant product information.
    2. If no relevant information is found, state that no matching products were found.
    3. Present the relevant product details clearly in your response.
    """,
    tools=[my_spanner_toolset],
)

```

### Why this matters for RAG

RAG is the standard way we stop AI models from hallucinating by grounding their answers in your actual data.
By adding this tool to Spanner, your AI can now directly "query" your database for relevant context in a way that truly understands the meaning behind a user's question, rather than just matching words.

Think about it as asking a librarian: "Do you have anything for a toddler learning to ride?" The librarian knows 'toddler' is related to 'small children' and 'learning to ride' is related to 'bikes,' so the output is related to what you’re looking for. By using `SpannerVectorStoreSettings` to configure your `SpannerToolset`, you are basically turning your Spanner database into that "smart librarian" that understands the meaning of your data.
