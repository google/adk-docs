# Native tools

These tools provide ready-to-use functionality in ADK that provide agents with
specialized capabilities without installing any other library.

## How to Use

1. **Import:** Import the desired tool from the tools module. This is
`agents.tools` in Python.
2. **Configure:** Initialize the tool, providing required parameters if any.
3. **Register:** Add the initialized tool to the **tools** list of your Agent.

Once added to an agent, the agent can decide to use the tool based on the **user
prompt** and its **instructions**. The framework handles the execution of the
tool when the agent calls it.

## Available Native tools

### BigQuery

These are a set of tools aimed to provide integration with BigQuery, namely:

* **`list_dataset_ids`**: Fetches BigQuery dataset ids present in a GCP project.
* **`get_dataset_info`**: Fetches metadata about a BigQuery dataset.
* **`list_table_ids`**: Fetches table ids present in a BigQuery dataset.
* **`get_table_info`**: Fetches metadata about a BigQuery table.
* **`execute_sql`**: Runs a SQL query in BigQuery and fetch the result.

They are packaged in the toolset `BigQueryToolset`.



```py
--8<-- "examples/python/snippets/tools/built-in-tools/bigquery.py"
```

## Use Built-in tools with other tools

For each root agent or single agent, the native tools can be used with other
non-built-in tools. For example, the following approach that uses
***a custom tool along with native tools*** within a single agent is supported:

=== "Python"

    ```py
    root_agent = Agent(
        name="RootAgent",
        model="gemini-2.0-flash",
        description="Root Agent",
        tools=[custom_function, BigQueryToolset()],
    )
    ```