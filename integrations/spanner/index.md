# Google Cloud Spanner tool for ADK

Supported in ADKPython v1.11.0

These are a set of tools aimed to provide integration with Spanner, namely:

- **`list_table_names`**: Fetches table names present in a GCP Spanner database.
- **`list_table_indexes`**: Fetches table indexes present in a GCP Spanner database.
- **`list_table_index_columns`**: Fetches table index columns present in a GCP Spanner database.
- **`list_named_schemas`**: Fetches named schema for a Spanner database.
- **`get_table_schema`**: Fetches Spanner database table schema and metadata information.
- **`execute_sql`**: Runs a SQL query in Spanner database and fetch the result.
- **`similarity_search`**: Similarity search in Spanner using a text query.

They are packaged in the toolset `SpannerToolset`.

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
# from google.adk.sessions import DatabaseSessionService
from google.adk.tools.google_tool import GoogleTool
from google.adk.tools.spanner import query_tool
from google.adk.tools.spanner.settings import SpannerToolSettings
from google.adk.tools.spanner.settings import Capabilities
from google.adk.tools.spanner.spanner_credentials import SpannerCredentialsConfig
from google.adk.tools.spanner.spanner_toolset import SpannerToolset
from google.genai import types
from google.adk.tools.tool_context import ToolContext
import google.auth
from google.auth.credentials import Credentials

# Define constants for this example agent
AGENT_NAME = "spanner_agent"
APP_NAME = "spanner_app"
USER_ID = "user1234"
SESSION_ID = "1234"
GEMINI_MODEL = "gemini-2.5-flash"

# Define Spanner tool config with read capability set to allowed.
tool_settings = SpannerToolSettings(capabilities=[Capabilities.DATA_READ])

# Define a credentials config - in this example we are using application default
# credentials
# https://cloud.google.com/docs/authentication/provide-credentials-adc
application_default_credentials, _ = google.auth.default()
credentials_config = SpannerCredentialsConfig(
    credentials=application_default_credentials
)

# Instantiate a Spanner toolset
spanner_toolset = SpannerToolset(
    credentials_config=credentials_config, spanner_tool_settings=tool_settings
)

# Optional
# Create a wrapped function tool for the agent on top of the built-in
# `execute_sql` tool in the Spanner toolset.
# For example, this customized tool can perform a dynamically-built query.
def count_rows_tool(
    table_name: str,
    credentials: Credentials,  # GoogleTool handles `credentials`
    settings: SpannerToolSettings,  # GoogleTool handles `settings`
    tool_context: ToolContext,  # GoogleTool handles `tool_context`
):
  """Counts the total number of rows for a specified table.

  Args:
    table_name: The name of the table for which to count rows.

  Returns:
      The total number of rows in the table.
  """

  # Replace the following settings for a specific Spanner database.
  PROJECT_ID = "<PROJECT_ID>"
  INSTANCE_ID = "<INSTANCE_ID>"
  DATABASE_ID = "<DATABASE_ID>"

  query = f"""
  SELECT count(*) FROM {table_name}
    """

  return query_tool.execute_sql(
      project_id=PROJECT_ID,
      instance_id=INSTANCE_ID,
      database_id=DATABASE_ID,
      query=query,
      credentials=credentials,
      settings=settings,
      tool_context=tool_context,
  )

# Agent Definition
spanner_agent = Agent(
    model=GEMINI_MODEL,
    name=AGENT_NAME,
    description=(
        "Agent to answer questions about Spanner database and execute SQL queries."
    ),
    instruction="""\
        You are a data assistant agent with access to several Spanner tools.
        Make use of those tools to answer the user's questions.
    """,
    tools=[
        spanner_toolset,
        # Add customized Spanner tool based on the built-in Spanner toolset.
        GoogleTool(
            func=count_rows_tool,
            credentials_config=credentials_config,
            tool_settings=tool_settings,
        ),
    ],
)


# Session and Runner
session_service = InMemorySessionService()

# Optionally, Spanner can be used as the Database Session Service for production.
# Note that it's suggested to use a dedicated instance/database for storing sessions.
# session_service_spanner_db_url = "spanner+spanner:///projects/PROJECT_ID/instances/INSTANCE_ID/databases/my-adk-session"
# session_service = DatabaseSessionService(db_url=session_service_spanner_db_url)

session = asyncio.run(
    session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
)
runner = Runner(
    agent=spanner_agent, app_name=APP_NAME, session_service=session_service
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

# Replace the Spanner database and table names below with your own.
call_agent("List all tables in projects/<PROJECT_ID>/instances/<INSTANCE_ID>/databases/<DATABASE_ID>")
call_agent("Describe the schema of <TABLE_NAME>")
call_agent("List the top 5 rows in <TABLE_NAME>")
```
