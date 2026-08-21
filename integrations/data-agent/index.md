# Google Cloud Data Agents tool for ADK

Supported in ADKPython v1.23.0

These are a set of tools aimed to provide integration with Data Agents powered by [Conversational Analytics API](https://docs.cloud.google.com/gemini/docs/conversational-analytics-api/overview).

Data Agents are AI-powered agents that help you analyze your data using natural language. When configuring a Data Agent, you can choose from supported data sources, including **BigQuery**, **Looker**, and **Looker Studio**.

**Prerequisites**

Before using these tools, you must build and configure your Data Agents in Google Cloud:

- [Build a data agent using HTTP and Python](https://docs.cloud.google.com/gemini/docs/conversational-analytics-api/build-agent-http)
- [Build a data agent using the Python SDK](https://docs.cloud.google.com/gemini/docs/conversational-analytics-api/build-agent-sdk)
- [Create a data agent in BigQuery Studio](https://docs.cloud.google.com/bigquery/docs/create-data-agents#create_a_data_agent)

The `DataAgentToolset` includes the following tools:

- **`list_accessible_data_agents`**: Lists Data Agents you have permission to access in the configured GCP project.
- **`get_data_agent_info`**: Retrieves details about a specific Data Agent given its full resource name.
- **`ask_data_agent`**: Chats with a specific Data Agent using natural language.

They are packaged in the toolset `DataAgentToolset`.

```py
# Copyright 2026 Google LLC
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
from google.adk.tools.data_agent.config import DataAgentToolConfig
from google.adk.tools.data_agent.credentials import DataAgentCredentialsConfig
from google.adk.tools.data_agent.data_agent_toolset import DataAgentToolset
from google.genai import types
import google.auth

# Define constants for this example agent
AGENT_NAME = "data_agent_example"
APP_NAME = "data_agent_app"
USER_ID = "user1234"
SESSION_ID = "1234"
GEMINI_MODEL = "gemini-2.5-flash"

# Define tool configuration
tool_config = DataAgentToolConfig(
    max_query_result_rows=100,
)

# Use Application Default Credentials (ADC)
# https://cloud.google.com/docs/authentication/provide-credentials-adc
application_default_credentials, _ = google.auth.default()
credentials_config = DataAgentCredentialsConfig(
    credentials=application_default_credentials
)

# Instantiate a Data Agent toolset
da_toolset = DataAgentToolset(
    credentials_config=credentials_config,
    data_agent_tool_config=tool_config,
    tool_filter=[
        "list_accessible_data_agents",
        "get_data_agent_info",
        "ask_data_agent",
    ],
)

# Agent Definition
data_agent = Agent(
    name=AGENT_NAME,
    model=GEMINI_MODEL,
    description="Agent to answer user questions using Data Agents.",
    instruction=(
        "## Persona\nYou are a helpful assistant that uses Data Agents"
        " to answer user questions about their data.\n\n"
    ),
    tools=[da_toolset],
)

# Session and Runner
session_service = InMemorySessionService()
session = asyncio.run(
    session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
)
runner = Runner(
    agent=data_agent, app_name=APP_NAME, session_service=session_service
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


call_agent("List accessible data agents in project <PROJECT_ID>.")
call_agent("Get information about <DATA_AGENT_NAME>.")
# The data agent in this example is configured with the BigQuery table:
# `bigquery-public-data.san_francisco.street_trees`
call_agent("Ask <DATA_AGENT_NAME> to count the rows in the table.")
call_agent("What are the columns in the table?")
call_agent("What are the top 5 tree species?")
call_agent("For those species, what is the distribution of legal status?")
```
