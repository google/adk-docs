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

## BigQuery AI/ML Skill

In addition to the tools listed above, the ADK provides a pre-packaged "skill" that helps the LLM use BigQuery's AI/ML features. You should prefer this skill over the high-level `forecast` and `detect_anomalies` tools. This skill guides the LLM to write standard SQL using `AI.*` functions (such as `AI.FORECAST`, `AI.CLASSIFY`, `AI.DETECT_ANOMALIES`, `AI.GENERATE`, etc.) via the `execute_sql` tool.

To use this skill, import the `get_bigquery_skill` function and the `SkillToolset` and pass them to your agent along with the `BigQueryToolset`.

```python
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.bigquery_skill import get_bigquery_skill
from google.adk.tools.skill_toolset import SkillToolset

# In addition to the BigQueryToolset, add the BigQuery skill.
bq_skill = get_bigquery_skill()
skill_toolset = SkillToolset(skills=[bq_skill])

# Pass both toolsets to your agent.
# Note that you still need to configure authentication for the BigQueryToolset.
# See the "Authentication" section for details.
agent = LlmAgent(tools=[bigquery_toolset, skill_toolset])
```

## Authentication

The `BigQueryToolset` supports several authentication mechanisms through `BigQueryCredentialsConfig`.

### Application Default Credentials

You should use this approach for local development and running on Google Cloud services, such as Cloud Run and GKE.

```python
import google.auth
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig

# Load Application Default Credentials
credentials, project_id = google.auth.default()

# Configure the toolset
credentials_config = BigQueryCredentialsConfig(credentials=credentials)
bigquery_toolset = BigQueryToolset(credentials_config=credentials_config)
```

### Service Account

You can explicitly provide a service account file or info.

```python
from google.oauth2 import service_account
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig

# Load Service Account credentials
credentials = service_account.Credentials.from_service_account_file('path/to/key.json')

# Configure the toolset
credentials_config = BigQueryCredentialsConfig(credentials=credentials)
bigquery_toolset = BigQueryToolset(credentials_config=credentials_config)
```

### External Access Token

For applications that need to act on behalf of an end-user, you can pass user credentials directly instantiated from an access token, such as from an OAuth2 flow or an external IDP.

```python
from google.oauth2.credentials import Credentials
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig

# Assume 'user_token' is obtained via an external OAuth flow
credentials = Credentials(token=user_token)

# Configure the toolset
credentials_config = BigQueryCredentialsConfig(credentials=credentials)
bigquery_toolset = BigQueryToolset(credentials_config=credentials_config)
```

### External Auth Providers

If you are integrating with an external authentication provider where the token is managed by the platform, such as Gemini Enterprise, use `external_access_token_key`.

```python
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig

# The key used to look up the access token in the session state
credentials_config = BigQueryCredentialsConfig(
    external_access_token_key="YOUR_AUTH_ID"
)
bigquery_toolset = BigQueryToolset(credentials_config=credentials_config)
```

### Interactive Auth (ADK Web)

When using the `adk web` interface for interactive sessions, you can provide OAuth 2.0 client credentials to trigger a login flow. This mechanism works for both local development and when your ADK agent is deployed to environments like Cloud Run.

```python
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig

# Provide OAuth 2.0 Client ID and Secret
credentials_config = BigQueryCredentialsConfig(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET"
)
bigquery_toolset = BigQueryToolset(credentials_config=credentials_config)
```

## Sample Code

The following sample code demonstrates how to use the `BigQueryToolset` in an ADK agent using Application Default Credentials (ADC).

```py
--8<-- "examples/python/snippets/tools/built-in-tools/bigquery.py"
```

## Sample Agent

For a complete, ready-to-run sample of a BigQuery-powered agent with detailed authentication examples, see the [BigQuery Sample Agent](https://github.com/google/adk-python/tree/main/contributing/samples/bigquery) on GitHub.

Note: If you want to access a BigQuery data agent as a tool, see [Data Agents tools for ADK](data-agent.md).
