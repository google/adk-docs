# Google Cloud Eventarc tool for ADK

Supported in ADKPython v2.6.0Experimental

The `EventarcToolset` allows agents to interact with [Google Cloud Eventarc](https://cloud.google.com/eventarc) to asynchronously publish structured [CloudEvents](https://cloudevents.io) to Eventarc Message Buses. The toolset provides built-in connection pooling and caching across invocations, and it supports both general-purpose event publishing and domain-specific, schema-enforced event tools.

Experimental

This feature is experimental and may be updated in future releases.

## Prerequisites

Before using the `EventarcToolset`, you need to complete the following setup steps:

1. **Enable the Eventarc APIs**: Enable the Eventarc and Eventarc Publishing APIs in your Google Cloud project:

   ```bash
   gcloud services enable eventarc.googleapis.com eventarcpublishing.googleapis.com
   ```

1. **Authenticate and authorize**: Ensure that the principal running the agent has the necessary IAM permissions to publish messages to Eventarc Message Buses (for example, the `roles/eventarc.publisher` role). For more information on Eventarc IAM roles, see the [Eventarc access control documentation](https://cloud.google.com/eventarc/docs/access-control). To set up local development credentials, see [Provide Application Default Credentials](https://cloud.google.com/docs/authentication/provide-credentials-adc).

1. **Create a Message Bus**: Create a target Eventarc Advanced Message Bus in your Google Cloud project to receive published events:

   ```bash
   gcloud eventarc message-buses create my-bus \
       --location=us-central1 \
       --logging-config=DEBUG
   ```

1. **Install required dependencies**: Install the `gcp` extra package to include the required Google Cloud Eventarc client library:

   ```bash
   pip install "google-adk[gcp]"
   ```

## Use with agent

The following example shows how to configure and equip an agent with the `EventarcToolset` to publish CloudEvents:

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
    " '{\"user\": \"alice\"}', datacontenttype 'application/json', and source"
    " '//my-service/auth'"
)
```

## Tools

The `EventarcToolset` includes the following general-purpose publishing tool by default:

### `publish_message`

Publishes a structured CloudEvent to a Google Cloud Eventarc Advanced Message Bus.

| Parameter                   | Type                 | Description                                                                                                                                                                           |
| --------------------------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bus`                       | `str`                | The full resource name of the Eventarc Message Bus (for example, `projects/my-project/locations/us-central1/messageBuses/my-bus`).                                                    |
| `type`                      | `str`                | The CloudEvents type identifier representing the occurrence (for example, `com.example.user.signup`).                                                                                 |
| `source`                    | `str`                | The CloudEvents source URI identifying the context in which an event happened (for example, `//my-service/auth`).                                                                     |
| `data`                      | `dict \| str \| Any` | (Optional) The event payload data to include in the CloudEvent.                                                                                                                       |
| `datacontenttype`           | `str`                | (Optional) The media type of `data` (for example, `application/json`). Defaults to `application/json` when dictionary or list data is provided, and `text/plain` for string payloads. |
| `subject`                   | `str`                | (Optional) The subject of the event in the context of the event producer.                                                                                                             |
| `id`                        | `str`                | (Optional) A unique identifier for the event. If not provided, a UUID is automatically generated.                                                                                     |
| `time`                      | `str`                | (Optional) Timestamp of when the occurrence happened in RFC 3339 format. If not provided, the current UTC timestamp is used.                                                          |
| `specversion`               | `str`                | (Optional) The CloudEvents specification version. Defaults to `1.0`.                                                                                                                  |
| `is_base64_encoded`         | `bool`               | (Optional) Whether `data` is base64-encoded binary data. Defaults to `False`.                                                                                                         |
| `include_tracing_extension` | `bool`               | (Optional) Whether to automatically extract and inject distributed tracing context into the CloudEvent's extension attributes. Defaults to `False`.                                   |
| `custom_attributes`         | `dict[str, str]`     | (Optional) Additional custom CloudEvent extension attributes to attach to the event.                                                                                                  |

## Domain-specific publish tools

In production multi-agent architectures, allowing an LLM to freely populate routing parameters (`bus`, `type`, `source`) can lead to hallucinated destinations or malformed event schemas. The `EventarcToolset.create_publish_tool` factory method enables you to create domain-specific, strict-schema publishing tools.

By creating a domain-specific tool, you can bind routing attributes using `CloudEventAttributesBinding` while enforcing a strict Pydantic model for the event payload (`payload_schema`). This guarantees that generated events match your business domain and are routed only to authorized message buses.

### Use with agent

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
# Evaluates attribute values dynamically at execution time from event payload, runtime context, or both.
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
```

### Parameters for `create_publish_tool`

The `create_publish_tool` method accepts the following keyword-only arguments:

| Parameter               | Type                                           | Description                                                                                                                                                                                                                                                                                                                                         |
| ----------------------- | ---------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`                  | `str`                                          | The function tool name exposed to the LLM (for example, `complete_outreach_static`).                                                                                                                                                                                                                                                                |
| `description`           | `str`                                          | A natural-language description instructing the LLM when to call this tool and what action it performs.                                                                                                                                                                                                                                              |
| `bus`                   | `str \| Callable[[Any], str] \| AgentProvided` | The target Eventarc Message Bus. Can be a static URI string, a runtime callable evaluated against tool context, or an `AgentProvided` instance to prompt the LLM to supply it.                                                                                                                                                                      |
| `ce_attributes_binding` | `CloudEventAttributesBinding`                  | Binding rules for CloudEvent attributes (`type`, `source`, `subject`, `datacontenttype`, `time`, `id`, `specversion`, `custom_attributes`).                                                                                                                                                                                                         |
| `payload_schema`        | `type[pydantic.BaseModel] \| None`             | (Optional) A Pydantic schema class defining the structured event payload. When specified, the tool signature requires an `event_data` parameter conforming to this model. If not provided (or `None`), no `event_data` parameter is added to the tool signature, and the tool publishes a notification-only CloudEvent without a data payload body. |

### CloudEvent attribute bindings and sentinels

The `CloudEventAttributesBinding` dataclass configures how individual CloudEvent fields are populated. Each attribute (`type`, `source`, `datacontenttype`, `subject`, `time`, `id`, `specversion`, `custom_attributes`) can be assigned one of the following binding mechanisms:

| Binding Type        | Example                                          | Exposed to LLM | Description                                                                                                                                                                       |
| ------------------- | ------------------------------------------------ | -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Static String**   | `type="vendor_outreach.completed"`               | No             | Enforces a fixed literal string. The attribute is hidden from the LLM signature and automatically applied on every call.                                                          |
| **Runtime Lambda**  | `source=lambda ctx: f"//agent/{ctx.session_id}"` | No             | A callable (`Callable[[Any], str]`) evaluated dynamically at execution time using the event payload, runtime context, or both. Hidden from the LLM signature.                     |
| **`AgentProvided`** | `subject=AgentProvided("Customer ID")`           | Yes            | Instructs ADK to expose the attribute as an explicit parameter in the function signature so the LLM can provide it. Accepts a `description` string.                               |
| **`MISSING`**       | `time=MISSING`                                   | No             | The default sentinel for optional attributes. Indicates default behavior applies (for example, automatically generating the current UTC timestamp for `time` or a UUID for `id`). |
| **`OMIT`**          | `time=OMIT`                                      | No             | Explicitly excludes an optional attribute from the generated CloudEvent. Mandatory attributes (`type`, `source`, `bus`, `id`, `specversion`) cannot be set to `OMIT`.             |

#### Example: Understanding `MISSING` versus `OMIT`

To understand the difference between `MISSING` and `OMIT`, consider how they affect an optional CloudEvent attribute such as `time`:

- **`time=MISSING` (default behavior)**: When you set `time=MISSING` (or leave `time` unspecified), the toolset applies its built-in default behavior. For `time`, it automatically generates and includes the current UTC timestamp formatted in RFC 3339 (for example, `"time": "2026-07-31T20:20:00Z"`).
- **`time=OMIT`**: When you explicitly set `time=OMIT`, the `time` field is completely excluded from the published CloudEvent payload. Use `OMIT` when downstream event consumers do not require or expect optional attributes.

```py
from google.adk.integrations.eventarc import (
    CloudEventAttributesBinding,
    MISSING,
    OMIT,
)

# 1. Using MISSING (default): CloudEvent automatically includes the current UTC timestamp
binding_with_timestamp = CloudEventAttributesBinding(
    type="vendor_outreach.completed",
    source="//my-agent/outreach",
    time=MISSING,  # Results in "time": "2026-07-31T20:20:00Z"
)

# 2. Using OMIT: CloudEvent will NOT include a 'time' attribute
binding_without_timestamp = CloudEventAttributesBinding(
    type="vendor_outreach.completed",
    source="//my-agent/outreach",
    time=OMIT,  # The 'time' field is excluded from the published event
)
```

## Additional resources

- [Google Cloud Eventarc documentation](https://cloud.google.com/eventarc/docs).
- [ADK Python GitHub repository](https://github.com/google/adk-python).
