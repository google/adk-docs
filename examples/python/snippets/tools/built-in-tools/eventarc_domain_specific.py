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
from typing import Any

from google.adk.agents import Agent
from google.adk.integrations.eventarc import AgentProvided
from google.adk.integrations.eventarc import CloudEventAttributesBinding
from google.adk.integrations.eventarc import EventarcCredentialsConfig
from google.adk.integrations.eventarc import EventarcToolConfig
from google.adk.integrations.eventarc import EventarcToolset
from google.adk.integrations.eventarc import OMIT
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import google.auth
import pydantic

# Define constants for this example agent
AGENT_NAME = "domain_specific_eventarc_agent"
APP_NAME = "eventarc_app"
USER_ID = "user1234"
SESSION_ID = "1234"
GEMINI_MODEL = "gemini-flash-latest"

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
BUS_NAME = os.getenv("EVENTARC_BUS_NAME", "outreach-bus")
BUS_URI = f"projects/{PROJECT_ID}/locations/us-central1/messageBuses/{BUS_NAME}"


# 1. Define a strictly validated Pydantic schema for the CloudEvent payload
class OutreachContext(pydantic.BaseModel):
  """Structured event payload for a completed customer outreach attempt."""

  customer_id: str = pydantic.Field(
      description="Unique identifier of the customer reached out to."
  )
  resolution_notes: str = pydantic.Field(
      description="Summary notes describing the outcome of the outreach call."
  )
  high_priority: bool = pydantic.Field(
      default=False,
      description="Whether this outreach requires urgent follow-up action.",
  )


# 2. Configure credentials and toolset
tool_config = EventarcToolConfig(project_id=PROJECT_ID)
application_default_credentials, _ = google.auth.default()
credentials_config = EventarcCredentialsConfig(
    credentials=application_default_credentials
)
eventarc_toolset = EventarcToolset(
    credentials_config=credentials_config, tool_config=tool_config
)

# 3. Create Domain-Specific Publish Tools

# Example A: Fully Statically Bound Tool (Safest)
# All routing parameters are locked down by the developer.
# The LLM only provides the structured data matching OutreachContext.
complete_outreach_static_tool = eventarc_toolset.create_publish_tool(
    name="complete_outreach_static",
    description="Logs a completed outreach attempt (statically bound routing).",
    payload_schema=OutreachContext,
    bus=BUS_URI,
    ce_attributes_binding=CloudEventAttributesBinding(
        type="vendor_outreach.completed",
        source="//my-agent/outreach",
        datacontenttype="application/json",
    ),
)

# Example B: Dynamically Bound Tool using AgentProvided and Sentinels
# Allows the LLM to provide the CloudEvent subject, while excluding optional attributes from the event payload.
complete_outreach_dynamic_tool = eventarc_toolset.create_publish_tool(
    name="complete_outreach_dynamic",
    description="Logs an outreach attempt with a dynamically provided subject.",
    payload_schema=OutreachContext,
    bus=BUS_URI,
    ce_attributes_binding=CloudEventAttributesBinding(
        type="vendor_outreach.completed",
        source="//my-agent/outreach",
        subject=AgentProvided("The unique customer ID being reached out to."),
        time=OMIT,
    ),
)


# Example C: Runtime Lambda Binding
# Evaluates attribute values dynamically at execution time from runtime context.
def resolve_source_from_context(context: Any) -> str:
  """Extracts the source URI dynamically from runtime tool execution context."""
  return f"//my-agent/session/{getattr(context, 'session_id', 'default')}"


complete_outreach_lambda_tool = eventarc_toolset.create_publish_tool(
    name="complete_outreach_lambda",
    description="Logs an outreach attempt using runtime context lambda binding.",
    payload_schema=OutreachContext,
    bus=BUS_URI,
    ce_attributes_binding=CloudEventAttributesBinding(
        type="vendor_outreach.completed",
        source=resolve_source_from_context,
    ),
)

# 4. Equip the agent with the domain-specific tools
root_agent = Agent(
    model=GEMINI_MODEL,
    name=AGENT_NAME,
    description="Agent for recording customer outreach completion events.",
    instruction="""\
        You are a customer outreach agent.
        Use the available outreach tools to record structured outreach events.
    """,
    tools=[
        complete_outreach_static_tool,
        complete_outreach_dynamic_tool,
        complete_outreach_lambda_tool,
    ],
)

# 5. Session and Runner
session_service = InMemorySessionService()
session = asyncio.run(
    session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
)
runner = Runner(
    agent=root_agent, app_name=APP_NAME, session_service=session_service
)


def call_agent(query: str):
  """Helper function to call the agent with a query."""
  content = types.Content(role="user", parts=[types.Part(text=query)])
  events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

  print("USER:", query)
  for event in events:
    if event.is_final_response():
      final_response = event.content.parts[0].text
      print("AGENT:", final_response)


# Example invocation
call_agent(
    "We successfully completed an outreach call with CUST-883. "
    "Resolution notes: All issues resolved. Not high priority."
)
