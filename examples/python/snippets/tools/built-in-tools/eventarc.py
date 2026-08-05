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
import os

from google.adk.agents import Agent
from google.adk.integrations.eventarc import EventarcCredentialsConfig
from google.adk.integrations.eventarc import EventarcToolConfig
from google.adk.integrations.eventarc import EventarcToolset
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import google.auth

# Define constants for this example agent
AGENT_NAME = "eventarc_agent"
APP_NAME = "eventarc_app"
USER_ID = "user1234"
SESSION_ID = "1234"
GEMINI_MODEL = "gemini-flash-latest"

# Define Eventarc tool config.
# You can optionally set the project_id here, or let the agent infer it from context/user input.
tool_config = EventarcToolConfig(project_id=os.getenv("GOOGLE_CLOUD_PROJECT"))

# Uses externally-managed Application Default Credentials (ADC) by default.
# This decouples authentication from the agent / tool lifecycle.
# https://cloud.google.com/docs/authentication/provide-credentials-adc
application_default_credentials, _ = google.auth.default()
credentials_config = EventarcCredentialsConfig(
    credentials=application_default_credentials
)

# Instantiate an Eventarc toolset
eventarc_toolset = EventarcToolset(
    credentials_config=credentials_config, tool_config=tool_config
)

# Agent Definition
root_agent = Agent(
    model=GEMINI_MODEL,
    name=AGENT_NAME,
    description=(
        "Agent to publish structured CloudEvents to Google Cloud Eventarc"
        " Message Buses."
    ),
    instruction="""\
        You are a cloud integration agent with access to Google Cloud Eventarc tools.
        You can publish structured CloudEvents to Eventarc Message Buses using the publish_message tool.
    """,
    tools=[eventarc_toolset],
)

# Session and Runner
session_service = InMemorySessionService()
session = asyncio.run(
    session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
)
runner = Runner(
    agent=root_agent, app_name=APP_NAME, session_service=session_service
)


# Agent Interaction
def call_agent(query: str):
  """Helper function to call the agent with a query."""
  content = types.Content(role="user", parts=[types.Part(text=query)])
  events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

  print("USER:", query)
  for event in events:
    if event.is_final_response():
      final_response = event.content.parts[0].text
      print("AGENT:", final_response)


# Example call to publish a CloudEvent
call_agent(
    "Publish an event of type 'com.example.user.signup' to bus"
    " 'projects/my-project/locations/us-central1/messageBuses/my-bus' with data"
    " '{\"user\": \"alice\"}' and source '//my-service/auth'"
)
