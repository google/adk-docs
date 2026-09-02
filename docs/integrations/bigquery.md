---
catalog_title: BigQuery Tools
catalog_description: Connect with BigQuery to retrieve data and perform analysis
catalog_icon: /integrations/assets/bigquery.png
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
* **`get_job_info`**: Fetches metadata information about a BigQuery job (slot usage, configuration, statistics, status, etc.).
* **`execute_sql`**: Runs a SQL query in BigQuery and fetch the result.
* **`forecast`**: Runs a BigQuery AI time series forecast using the `AI.FORECAST` function.
* **`analyze_contribution`**: Performs BigQuery ML contribution analysis to understand what drives changes in a metric.
* **`detect_anomalies`**: Trains an ARIMA_PLUS model and detects anomalies in time series data.
* **`ask_data_insights`**: Answers questions about data in BigQuery tables using natural language.
* **`search_catalog`**: Finds BigQuery datasets and tables using natural language semantic search via Dataplex.

They are packaged in the toolset `BigQueryToolset`.

## Authentication

The `BigQueryToolset` supports several authentication mechanisms through `BigQueryCredentialsConfig`.

### Application Default Credentials

You should use this approach for local development and running on Google Cloud services, such as Cloud Run and GKE.

```python
--8<-- "examples/inline/python/integrations/bigquery/001-application-default-credentials.py"
```

### Service Account

You can explicitly provide a service account file or info.

```python
--8<-- "examples/inline/python/integrations/bigquery/002-service-account.py"
```

### External Access Token

For applications that need to act on behalf of an end-user, you can pass user credentials directly instantiated from an access token, such as from an OAuth2 flow or an external IDP.

```python
--8<-- "examples/inline/python/integrations/bigquery/003-external-access-token.py"
```

### External Auth Providers

If you are integrating with an external authentication provider where the token is managed by the platform, such as Gemini Enterprise, use `external_access_token_key`.

```python
--8<-- "examples/inline/python/integrations/bigquery/004-external-auth-providers.py"
```

### Interactive Auth (ADK Web)

When using the `adk web` interface for interactive sessions, you can provide OAuth 2.0 client credentials to trigger a login flow. This mechanism works for both local development and when your ADK agent is deployed to environments like Cloud Run.

```python
--8<-- "examples/inline/python/integrations/bigquery/005-interactive-auth-adk-web.py"
```

## Sample Code

The following sample code demonstrates how to use the `BigQueryToolset` in an ADK agent using Application Default Credentials (ADC).

```py
--8<-- "examples/python/snippets/tools/built-in-tools/bigquery.py"
```

## Sample Agent

For a complete, ready-to-run sample of a BigQuery-powered agent with detailed authentication examples, see the [BigQuery Sample Agent](https://github.com/google/adk-python/tree/main/contributing/samples/integrations/bigquery) on GitHub.

Note: If you want to access a BigQuery data agent as a tool, see [Data Agents tools for ADK](data-agent.md).
