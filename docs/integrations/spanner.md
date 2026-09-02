---
catalog_title: Spanner Tools
catalog_description: Interact with Spanner to retrieve data, search, and execute SQL
catalog_icon: /integrations/assets/spanner.png
catalog_tags: ["data","google"]
---

# Google Cloud Spanner tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.11.0</span><span class="lst-preview">Experimental</span>
</div>

[Google Cloud Spanner](https://cloud.google.com/spanner) is a fully managed,
distributed database with support for SQL and vector search. The ADK Spanner
tools let your agent explore database schemas, run SQL queries, and perform
vector similarity search against your Spanner data.

!!! example "Experimental"
    This feature is experimental and may be updated in future releases.

## Available tools

The `SpannerToolset` provides the following tools:

- **`list_table_names`**: Fetches table names present in a GCP Spanner database.
- **`list_table_indexes`**: Fetches table indexes present in a GCP Spanner
  database.
- **`list_table_index_columns`**: Fetches table index columns present in a GCP
  Spanner database.
- **`list_named_schemas`**: Fetches named schema for a Spanner database.
- **`get_table_schema`**: Fetches Spanner database table schema and metadata
  information.
- **`execute_sql`**: Runs a SQL query in Spanner database and fetch the result.
- **`similarity_search`**: Similarity search in Spanner using a text query.

## Use with agent

```py
--8<-- "examples/python/snippets/tools/built-in-tools/spanner.py"
```

## Vector similarity search

The `vector_store_similarity_search` tool enables agents to perform semantic
searches against a Spanner table configured as a vector store. This capability
is essential for building contextually aware RAG applications; it allows AI
models to retrieve database context based on semantic meaning rather than exact
keyword matches. By configuring `SpannerVectorStoreSettings`, your agents can
better understand the intent behind user queries and ground their responses in
the most relevant Spanner data.

The following example configures a Spanner table as a vector store and wires the
`vector_store_similarity_search` tool into a RAG agent:

```py
--8<-- "examples/inline/python/integrations/spanner/001-vector-similarity-search.py"
```

### Configuration

The `SpannerVectorStoreSettings` class used above defines how
`vector_store_similarity_search` operates. It accepts the following parameters:

#### Required parameters

- **`project_id`**: Your Google Cloud Project ID required for authentication
  context.
- **`instance_id`**: The Spanner instance ID.
- **`database_id`**: The Spanner database ID.
- **`table_name`**: The Spanner table containing the vector embeddings.
- **`embedding_column`**: The `ARRAY<FLOAT>` or `ARRAY<DOUBLE>` column where the
  vector embeddings are stored.
- **`content_column`**: The column containing the original text or content to be
  retrieved.
- **`vector_length`**: The dimensionality of your embedding vectors that must
  match your model.
- **`vertex_ai_embedding_model_name`**: The model used to generate the
  embeddings, for example "text-embedding-005".

#### Optional parameters

- **`selected_columns`**: A list of columns you can include in the search
  results, such as metadata or identifiers.
- **`nearest_neighbors_algorithm`**: The algorithm you use for the search, such
  as `EXACT_NEAREST_NEIGHBORS` and `APPROXIMATE_NEAREST_NEIGHBORS`.
    - **`num_leaves_to_search`**: Number of index leaf nodes searched. Only used
      with `APPROXIMATE_NEAREST_NEIGHBORS`.
    - **`vector_search_index_settings`**: Vector index settings. Only required with
      `APPROXIMATE_NEAREST_NEIGHBORS`.
- **`top_k`**: The number of nearest neighbors to retrieve per query.
- **`distance_type`**: The distance metric used for similarity calculation, such
  as `COSINE` or `EUCLIDEAN`.
- **`additional_filter`**: An optional SQL filter string to apply during the
  search, for example: "inventoryCount > 0".

## Spanner Admin Toolset

The `SpannerAdminToolset` enables administrative operations on your Spanner instances and databases. Note that this requires a separate library import. 

!!! warning "Use with caution"

    This toolset can create, inspect, and modify Spanner instances and
    databases, grant access carefully. Ensure that the executing environment
    (such as Application Default Credentials or Service Account keys) is
    restricted only to authorized projects and uses the minimum necessary IAM
    permissions such as, roles/spanner.admin.

### Available tools

* **`list_instances`**: Lists Spanner instances within a project.
* **`get_instance`**: Retrieves details of a Spanner instance.
* **`create_database`**: Creates a new Spanner database.
* **`list_databases`**: Lists Spanner databases within an instance.
* **`create_instance`**: Creates a new Spanner instance.
* **`list_instance_configs`**: Lists available Spanner instance configs.
* **`get_instance_config`**: Retrieves details of a Spanner instance config.

### Configuration

Set your required environment variables before using this toolset:

- `SPANNER_PROJECT`: The GCP project ID for operations.
- `SPANNER_INSTANCE` (Optional): The default Spanner instance ID.
- `SPANNER_DATABASE` (Optional): The default database ID.

### Use with agent
Initialize the `SpannerAdminToolset` to access Google Cloud Spanner management features. Then, pass it into the `tools` list of your `LlmAgent` to enable your agent to manage Spanner resources.

```python
--8<-- "examples/inline/python/integrations/spanner/002-use-with-agent.py"
```
