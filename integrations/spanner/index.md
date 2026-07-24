# Google Cloud Spanner tool for ADK

Supported in ADKPython v1.11.0Experimental

[Google Cloud Spanner](https://cloud.google.com/spanner) is a fully managed, distributed database with support for SQL and vector search. The ADK Spanner tools let your agent explore database schemas, run SQL queries, and perform vector similarity search against your Spanner data.

Experimental

This feature is experimental and may be updated in future releases.

## Available tools

The `SpannerToolset` provides the following tools:

- **`list_table_names`**: Fetches table names present in a GCP Spanner database.
- **`list_table_indexes`**: Fetches table indexes present in a GCP Spanner database.
- **`list_table_index_columns`**: Fetches table index columns present in a GCP Spanner database.
- **`list_named_schemas`**: Fetches named schema for a Spanner database.
- **`get_table_schema`**: Fetches Spanner database table schema and metadata information.
- **`execute_sql`**: Runs a SQL query in Spanner database and fetch the result.
- **`similarity_search`**: Similarity search in Spanner using a text query.

## Use with agent

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
    instruction="""
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

## Vector similarity search

The `vector_store_similarity_search` tool enables agents to perform semantic searches against a Spanner table configured as a vector store. This capability is essential for building contextually aware RAG applications; it allows AI models to retrieve database context based on semantic meaning rather than exact keyword matches. By configuring `SpannerVectorStoreSettings`, your agents can better understand the intent behind user queries and ground their responses in the most relevant Spanner data.

The following example configures a Spanner table as a vector store and wires the `vector_store_similarity_search` tool into a RAG agent:

```py
from google.adk.agents import LlmAgent
from google.adk.tools.spanner import SpannerCredentialsConfig, SpannerToolset
from google.adk.tools.spanner.settings import (
    Capabilities,
    SpannerToolSettings,
    SpannerVectorStoreSettings,
)

# 1. Define Spanner tool config with vector store settings
my_vector_store_settings = SpannerVectorStoreSettings(
    project_id="your-gcp-project",
    instance_id="your-spanner-instance",
    database_id="your-database",
    table_name="my_products",
    content_column="productDescription",
    embedding_column="productDescriptionEmbedding",
    vector_length=768,
    vertex_ai_embedding_model_name="text-embedding-005",
    selected_columns=["productId", "productName", "productDescription"],
    nearest_neighbors_algorithm="EXACT_NEAREST_NEIGHBORS",
    top_k=3,
    distance_type="COSINE",
    additional_filter="inventoryCount > 0",
)

my_tool_settings = SpannerToolSettings(
    capabilities=[Capabilities.DATA_READ],
    vector_store_settings=my_vector_store_settings,
)

# 2. Initialize the Spanner toolset
credentials_config = SpannerCredentialsConfig()
my_spanner_toolset = SpannerToolset(
    credentials_config=credentials_config,
    spanner_tool_settings=my_tool_settings,
    tool_filter=["vector_store_similarity_search"],
)

# 3. Use the toolset in your RAG agent
my_rag_agent = LlmAgent(
    model="gemini-flash-latest",
    name="product_search_agent",
    instruction="""
    You are a helpful assistant that answers user questions by finding similar products.
    1. Always use the `vector_store_similarity_search` tool to find relevant product information.
    2. If no relevant information is found, state that no matching products were found.
    3. Present the relevant product details clearly in your response.
    """,
    tools=[my_spanner_toolset],
)
```

### Configuration

The `SpannerVectorStoreSettings` class used above defines how `vector_store_similarity_search` operates. It accepts the following parameters:

#### Required parameters

- **`project_id`**: Your Google Cloud Project ID required for authentication context.
- **`instance_id`**: The Spanner instance ID.
- **`database_id`**: The Spanner database ID.
- **`table_name`**: The Spanner table containing the vector embeddings.
- **`embedding_column`**: The `ARRAY<FLOAT>` or `ARRAY<DOUBLE>` column where the vector embeddings are stored.
- **`content_column`**: The column containing the original text or content to be retrieved.
- **`vector_length`**: The dimensionality of your embedding vectors that must match your model.
- **`vertex_ai_embedding_model_name`**: The model used to generate the embeddings, for example "text-embedding-005".

#### Optional parameters

- **`selected_columns`**: A list of columns you can include in the search results, such as metadata or identifiers.
- **`nearest_neighbors_algorithm`**: The algorithm you use for the search, such as `EXACT_NEAREST_NEIGHBORS` and `APPROXIMATE_NEAREST_NEIGHBORS`.
  - **`num_leaves_to_search`**: Number of index leaf nodes searched. Only used with `APPROXIMATE_NEAREST_NEIGHBORS`.
  - **`vector_search_index_settings`**: Vector index settings. Only required with `APPROXIMATE_NEAREST_NEIGHBORS`.
- **`top_k`**: The number of nearest neighbors to retrieve per query.
- **`distance_type`**: The distance metric used for similarity calculation, such as `COSINE` or `EUCLIDEAN`.
- **`additional_filter`**: An optional SQL filter string to apply during the search, for example: "inventoryCount > 0".
