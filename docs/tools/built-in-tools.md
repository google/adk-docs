# Built-in tools

These built-in tools provide ready-to-use functionality such as Google Search or
code executors that provide agents with common capabilities. For instance, an
agent that needs to retrieve information from the web can directly use the
**google\_search** tool without any additional setup.

## How to Use

1. **Import:** Import the desired tool from the tools module. This is `agents.tools` in Python or `com.google.adk.tools` in Java.
2. **Configure:** Initialize the tool, providing required parameters if any.
3. **Register:** Add the initialized tool to the **tools** list of your Agent.

Once added to an agent, the agent can decide to use the tool based on the **user
prompt** and its **instructions**. The framework handles the execution of the
tool when the agent calls it. Important: check the ***Limitations*** section of this page.

## Available Built-in tools

Note: Java only supports Google Search and Code Execution tools currently.

### Google Search

The `google_search` tool allows the agent to perform web searches using Google Search. The `google_search` tool is only compatible with Gemini 2 models. For further details of the tool, see [Understanding Google Search grounding](../grounding/google_search_grounding.md).

!!! warning "Additional requirements when using the `google_search` tool"
    When you use grounding with Google Search, and you receive Search suggestions in your response, you must display the Search suggestions in production and in your applications.
    For more information on grounding with Google Search, see Grounding with Google Search documentation for [Google AI Studio](https://ai.google.dev/gemini-api/docs/grounding/search-suggestions) or [Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-search-suggestions). The UI code (HTML) is returned in the Gemini response as `renderedContent`, and you will need to show the HTML in your app, in accordance with the policy.



### Code Execution

The `built_in_code_execution` tool enables the agent to execute code,
specifically when using Gemini 2 models. This allows the model to perform tasks
like calculations, data manipulation, or running small scripts.



### GKE Code Executor

The GKE Code Executor (`GkeCodeExecutor`) provides a secure and scalable method
for running LLM-generated code by leveraging the GKE (Google Kubernetes Engine)
Sandbox environment, which uses gVisor for workload isolation. For each code
execution request, it dynamically creates an ephemeral, sandboxed Kubernetes Job
with a hardened Pod configuration. You should use this executor for production
environments on GKE where security and isolation are critical.

#### How it Works

When a request to execute code is made, the `GkeCodeExecutor` performs the following steps:

1.  **Creates a ConfigMap:** A Kubernetes ConfigMap is created to store the Python code that needs to be executed.
2.  **Creates a Sandboxed Pod:** A new Kubernetes Job is created, which in turn creates a Pod with a hardened security context and the gVisor runtime enabled. The code from the ConfigMap is mounted into this Pod.
3.  **Executes the Code:** The code is executed within the sandboxed Pod, isolated from the underlying node and other workloads.
4.  **Retrieves the Result:** The standard output and error streams from the execution are captured from the Pod's logs.
5.  **Cleans Up Resources:** Once the execution is complete, the Job and the associated ConfigMap are automatically deleted, ensuring that no artifacts are left behind.

#### Key Benefits

*   **Enhanced Security:** Code is executed in a gVisor-sandboxed environment with kernel-level isolation.
*   **Ephemeral Environments:** Each code execution runs in its own ephemeral Pod, to prevent state transfer between executions.
*   **Resource Control:** You can configure CPU and memory limits for the execution Pods to prevent resource abuse.
*   **Scalability:** Allows you to run a large number of code executions in parallel, with GKE handling the scheduling and scaling of the underlying nodes.

#### System requirements

The following requirements must be met to successfully deploy your ADK project
with the GKE Code Executor tool:

- GKE cluster with a **gVisor-enabled node pool**.
- Agent's service account requires specific **RBAC permissions**, which allow it to:
    - Create, watch, and delete **Jobs** for each execution request.
    - Manage **ConfigMaps** to inject code into the Job's pod.
    - List **Pods** and read their **logs** to retrieve the execution result
- Install the client library with GKE extras: `pip install google-adk[gke]`

For a complete, ready-to-use configuration, see the 
[deployment_rbac.yaml](https://github.com/google/adk-python/blob/main/contributing/samples/gke_agent_sandbox/deployment_rbac.yaml)
sample. For more information on deploying ADK workflows to GKE, see
[Deploy to Google Kubernetes Engine (GKE)](/adk-docs/deploy/gke/).



#### Configuration parameters

The `GkeCodeExecutor` can be configured with the following parameters:

| Parameter            | Type   | Description                                                                             |
| -------------------- | ------ | --------------------------------------------------------------------------------------- |
| `namespace`          | `str`  | Kubernetes namespace where the execution Jobs will be created. Defaults to `"default"`. |
| `image`              | `str`  | Container image to use for the execution Pod. Defaults to `"python:3.11-slim"`.         |
| `timeout_seconds`    | `int`  | Timeout in seconds for the code execution. Defaults to `300`.                           |
| `cpu_requested`      | `str`  | Amount of CPU to request for the execution Pod. Defaults to `"200m"`.                   |
| `mem_requested`      | `str`  | Amount of memory to request for the execution Pod. Defaults to `"256Mi"`.               |
| `cpu_limit`          | `str`  | Maximum amount of CPU the execution Pod can use. Defaults to `"500m"`.                  |
| `mem_limit`          | `str`  | Maximum amount of memory the execution Pod can use. Defaults to `"512Mi"`.              |
| `kubeconfig_path`    | `str`  | Path to a kubeconfig file to use for authentication. Falls back to in-cluster config or the default local kubeconfig. |
| `kubeconfig_context` | `str`  | The `kubeconfig` context to use.  |

### Vertex AI RAG Engine

The `vertex_ai_rag_retrieval` tool allows the agent to perform private data retrieval using Vertex
AI RAG Engine.

When you use grounding with Vertex AI RAG Engine, you need to prepare a RAG corpus before hand.
Please refer to the [RAG ADK agent sample](https://github.com/google/adk-samples/blob/main/python/agents/RAG/rag/shared_libraries/prepare_corpus_and_data.py) or [Vertex AI RAG Engine page](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-quickstart) for setting it up.



### Vertex AI Search

The `vertex_ai_search_tool` uses Google Cloud Vertex AI Search, enabling the
agent to search across your private, configured data stores (e.g., internal
documents, company policies, knowledge bases). This built-in tool requires you
to provide the specific data store ID during configuration. For further details of the tool, see [Understanding Vertex AI Search grounding](../grounding/vertex_ai_search_grounding.md).




### BigQuery

These are a set of tools aimed to provide integration with BigQuery, namely:

* **`list_dataset_ids`**: Fetches BigQuery dataset ids present in a GCP project.
* **`get_dataset_info`**: Fetches metadata about a BigQuery dataset.
* **`list_table_ids`**: Fetches table ids present in a BigQuery dataset.
* **`get_table_info`**: Fetches metadata about a BigQuery table.
* **`execute_sql`**: Runs a SQL query in BigQuery and fetch the result. This tool now includes a `dry_run` parameter. If set to `True`, the query will be validated by BigQuery but not actually executed, returning information about the query's validity and potential cost.
* **`forecast`**: Runs a BigQuery AI time series forecast using the `AI.FORECAST` function.
* **`ask_data_insights`**: Answers questions about data in BigQuery tables using natural language.
* **`analyze_contribution`**: Runs a BigQuery ML contribution analysis using `ML.CREATE_MODEL` and `ML.GET_INSIGHTS` to identify the dimensions that contribute most significantly to a given metric.

They are packaged in the toolset `BigQueryToolset`.






### Spanner

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

### Customizable Template and Parameterized SQL

In addition to the pre-built Spanner tools, you can create your own customized Spanner query tools using template or parameterized SQL. This allows you to define specific queries that your agent can execute.

#### Template SQL

You can create a function that builds a SQL query string using an f-string or other string formatting method. This approach is flexible but can be vulnerable to SQL injection if you are not careful about how you handle user input. It is recommended to add additional checks or callbacks to validate the input.

```python
from google.adk.tools.spanner import utils as spanner_tool_utils

def count_rows_in_table(
    table_name: str,
    credentials,
    settings,
    tool_context,
):
  """Counts the total number of rows for a specified table."""

  # Example of adding additional checks:
  # if table_name not in ["table1", "table2"]:
  #   raise ValueError("Table name is not allowed.")

  sql_template = f"SELECT COUNT(*) FROM {table_name}"

  return spanner_tool_utils.execute_sql(
      project_id="<PROJECT_ID>",
      instance_id="<INSTANCE_ID>",
      database_id="<DATABASE_ID>",
      query=sql_template,
      credentials=credentials,
      settings=settings,
      tool_context=tool_context,
  )
```

#### Parameterized SQL

A more secure approach is to use a parameterized SQL query. This helps to prevent SQL injection by separating the query logic from the user-provided values.

```python
from google.adk.tools.spanner import utils as spanner_tool_utils
from google.cloud.spanner_v1 import param_types

def search_hotels(
    location_name: str,
    credentials,
    settings,
    tool_context,
):
  """Search hotels for a specific location."""

  sql_template = """
      SELECT name, rating, description FROM hotels
      WHERE location_name = @location_name
      """
  return spanner_tool_utils.execute_sql(
      project_id="<PROJECT_ID>",
      instance_id="<INSTANCE_ID>",
      database_id="<DATABASE_ID>",
      query=sql_template,
      credentials=credentials,
      settings=settings,
      tool_context=tool_context,
      params={"location_name": location_name},
      params_types={"location_name": spanner_param_types.STRING},
  )
```


### Bigtable

These are a set of tools aimed to provide integration with Bigtable, namely:

* **`list_instances`**: Fetches Bigtable instances in a Google Cloud project.
* **`get_instance_info`**: Fetches metadata instance information in a Google Cloud project.
* **`list_tables`**: Fetches tables in a GCP Bigtable instance.
* **`get_table_info`**: Fetches metadata table information in a GCP Bigtable.
* **`execute_sql`**: Runs a SQL query in Bigtable table and fetch the result.

They are packaged in the toolset `BigtableToolset`.





## Use Built-in tools with other tools

The following code sample demonstrates how to use multiple built-in tools or how
to use built-in tools with other tools by using multiple agents:




### Limitations

!!! warning

    Currently, for each root agent or single agent, only one built-in tool is
    supported. No other tools of any type can be used in the same agent.

 For example, the following approach that uses ***a built-in tool along with
 other tools*** within a single agent is **not** currently supported:




!!! warning

    Built-in tools cannot be used within a sub-agent.

For example, the following approach that uses built-in tools within sub-agents
is **not** currently supported:

