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

# ---8<--- [start:just_code]
import asyncio

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.data_agent import DataAgentCredentialsConfig
from google.adk.tools.data_agent import DataAgentToolset
from google.adk.tools.data_agent.config import DataAgentToolConfig
from google.genai import types
import google.auth

# Define constants for this example agent
AGENT_NAME = "data_agent_example"
APP_NAME = "data_agent_app"
USER_ID = "user1234"
SESSION_ID = "1234"
GEMINI_MODEL = "gemini-flash-latest"

# Define tool configuration
# Set `enable_data_agent_modification=True` to also expose `create_data_agent`,
# `update_data_agent`, and `delete_data_agent`.
tool_config = DataAgentToolConfig(
    max_query_result_rows=100,
    enable_data_agent_modification=False,
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
)

# Agent Definition
data_agent = Agent(
    name=AGENT_NAME,
    model=GEMINI_MODEL,
    description="Agent to answer user questions using data agents.",
    instruction=(
        "## Persona\nYou are a helpful assistant that uses data agents"
        " to answer user questions about their data.\n\n"
    ),
    tools=[da_toolset],
)


# Session and Runner
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    return Runner(
        agent=data_agent, app_name=APP_NAME, session_service=session_service
    )


# Agent Interaction
async def call_agent_async(runner, query):
    """
    Helper function to call the agent with a query.
    """
    content = types.Content(role="user", parts=[types.Part(text=query)])
    events = runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=content
    )

    print("USER:", query)
    async for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("AGENT:", final_response)


async def main():
    runner = await setup_session_and_runner()
    # Replace `<PROJECT_ID>` with your Google Cloud project ID, and replace
    # `<DATA_AGENT_NAME>` with a full resource name in the format:
    # `projects/{project}/locations/{location}/dataAgents/{agent}`
    await call_agent_async(
        runner, "List accessible data agents in project <PROJECT_ID>."
    )
    await call_agent_async(runner, "Get information about <DATA_AGENT_NAME>.")
    # The data agent in this example is configured with the BigQuery table:
    # `bigquery-public-data.san_francisco.street_trees`
    await call_agent_async(
        runner, "Ask <DATA_AGENT_NAME> to count the rows in the table."
    )
    await call_agent_async(runner, "What are the columns in the table?")
    await call_agent_async(runner, "What are the top 5 tree species?")
    await call_agent_async(
        runner, "For those species, what is the distribution of legal status?"
    )
# ---8<--- [end:just_code]

# Note: In Colab or another notebook, an event loop is already running, so call
# `await main()` directly instead of `asyncio.run(main())`.
asyncio.run(main())
