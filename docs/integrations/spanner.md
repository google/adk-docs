---
catalog_title: Spanner Tools
catalog_description: Interact with Spanner to retrieve data, search, and execute SQL
catalog_icon: /adk-docs/integrations/assets/spanner.png
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

