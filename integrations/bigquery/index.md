# BigQuery tool for ADK

Supported in ADKPython v1.1.0

These are a set of tools aimed to provide integration with BigQuery, namely:

- **`list_dataset_ids`**: Fetches BigQuery dataset ids present in a GCP project.
- **`get_dataset_info`**: Fetches metadata about a BigQuery dataset.
- **`list_table_ids`**: Fetches table ids present in a BigQuery dataset.
- **`get_table_info`**: Fetches metadata about a BigQuery table.
- **`get_job_info`**: Fetches metadata information about a BigQuery job (slot usage, configuration, statistics, status, etc.).
- **`execute_sql`**: Runs a SQL query in BigQuery and fetch the result.
- **`forecast`**: Runs a BigQuery AI time series forecast using the `AI.FORECAST` function.
- **`analyze_contribution`**: Performs BigQuery ML contribution analysis to understand what drives changes in a metric.
- **`detect_anomalies`**: Trains an ARIMA_PLUS model and detects anomalies in time series data.
- **`ask_data_insights`**: Answers questions about data in BigQuery tables using natural language.
- **`search_catalog`**: Finds BigQuery datasets and tables using natural language semantic search via Dataplex.

They are packaged in the toolset `BigQueryToolset`.

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
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.bigquery import BigQueryCredentialsConfig
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig
from google.adk.tools.bigquery.config import WriteMode
from google.genai import types
import google.auth

# Define constants for this example agent
AGENT_NAME = "bigquery_agent"
APP_NAME = "bigquery_app"
USER_ID = "user1234"
SESSION_ID = "1234"
GEMINI_MODEL = "gemini-2.0-flash"

# Define a tool configuration to block any write operations
tool_config = BigQueryToolConfig(write_mode=WriteMode.BLOCKED)

# Use Application Default Credentials (ADC) for BigQuery authentication
# https://cloud.google.com/docs/authentication/provide-credentials-adc
application_default_credentials, _ = google.auth.default()
credentials_config = BigQueryCredentialsConfig(
    credentials=application_default_credentials
)

# Instantiate a BigQuery toolset
bigquery_toolset = BigQueryToolset(
    credentials_config=credentials_config, bigquery_tool_config=tool_config
)

# Agent Definition
bigquery_agent = Agent(
    model=GEMINI_MODEL,
    name=AGENT_NAME,
    description=(
        "Agent to answer questions about BigQuery data and models and execute"
        " SQL queries."
    ),
    instruction="""\
        You are a data science agent with access to several BigQuery tools.
        Make use of those tools to answer the user's questions.
    """,
    tools=[bigquery_toolset],
)

# Session and Runner
session_service = InMemorySessionService()
session = asyncio.run(
    session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
)
runner = Runner(
    agent=bigquery_agent, app_name=APP_NAME, session_service=session_service
)


# Agent Interaction
def call_agent(query):
    """
    Helper function to call the agent with a query.
    """
    content = types.Content(role="user", parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    print("USER:", query)
    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("AGENT:", final_response)


call_agent("Are there any ml datasets in bigquery-public-data project?")
call_agent("Tell me more about ml_datasets.")
call_agent("Which all tables does it have?")
call_agent("Tell me more about the census_adult_income table.")
call_agent("How many rows are there per income bracket?")
call_agent(
    "What is the statistical correlation between education_num, age, and the income_bracket?"
)
```

## Sample Agent

For a complete, ready-to-run sample of a BigQuery-powered agent with detailed authentication examples, see the [BigQuery Sample Agent](https://github.com/google/adk-python/tree/main/contributing/samples/bigquery) on GitHub.

Note: If you want to access a BigQuery data agent as a tool, see [Data Agents tools for ADK](https://adk.dev/integrations/data-agent/index.md).
