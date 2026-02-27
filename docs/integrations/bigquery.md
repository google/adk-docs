---
catalog_title: BigQuery Tools
catalog_description: Connect with BigQuery to retrieve data and perform analysis
catalog_icon: /adk-docs/integrations/assets/bigquery.png
catalog_tags: ["data", "google"]
---

# BigQuery tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.1.0</span>
</div>

These are a set of tools aimed to provide integration with BigQuery, namely:

* **`list_dataset_ids`**: Fetches BigQuery dataset ids present in a GCP project.
* **`get_dataset_info`**: Fetches metadata about a BigQuery dataset.
* **`list_table_ids`**: Fetches table ids present in a BigQuery dataset.
* **`get_table_info`**: Fetches metadata about a BigQuery table.
* **`execute_sql`**: Runs a SQL query in BigQuery and fetch the result.
* **`forecast`**: Runs a BigQuery AI time series forecast using the `AI.FORECAST` function.
* **`ask_data_insights`**: Answers questions about data in BigQuery tables using natural language.

They are packaged in the toolset `BigQueryToolset`.

```py
--8<-- "examples/python/snippets/tools/built-in-tools/bigquery.py"
```

Note: If you want to access a BigQuery data agent as a tool, see [Data Agents tools for ADK](data-agent.md).
