# Bigtable database tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.12.0</span>
</div>

These are a set of tools aimed to provide integration with Bigtable, namely:

* **`list_instances`**: Fetches Bigtable instances in a Google Cloud project.
* **`get_instance_info`**: Fetches metadata instance information in a Google Cloud project.
* **`list_tables`**: Fetches tables in a GCP Bigtable instance.
* **`get_table_info`**: Fetches metadata table information in a GCP Bigtable.
* **`execute_sql`**: Runs a SQL query in Bigtable table and fetch the result.

They are packaged in the toolset `BigtableToolset`.

```py
--8<-- "examples/python/snippets/tools/built-in-tools/bigtable.py"
```

