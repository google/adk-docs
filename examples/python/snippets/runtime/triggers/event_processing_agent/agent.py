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

# --8<-- [start:event_processor]
import json

from google.adk.agents import LlmAgent


def parse_event(raw_event: str) -> dict:
    """Parse and extract structured data from a trigger event.

    Trigger endpoints deliver events as a JSON string with 'data' and
    'attributes' fields. This tool extracts those fields so the agent
    can reason about the event contents.
    """
    try:
        event = json.loads(raw_event)
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse event JSON: {e}"}
    return {
        "data": event.get("data"),
        "attributes": event.get("attributes", {}),
    }


root_agent = LlmAgent(
    model="gemini-flash-latest",
    name="event_processor",
    instruction="""You are an event-processing agent that handles incoming
events from Pub/Sub and Eventarc triggers.

When you receive an event:
1. Use the `parse_event` tool to extract the event data and attributes.
2. Analyze the event contents and determine what action to take.
3. Summarize what you found and what action you would recommend.

Be concise and structured in your responses.""",
    tools=[parse_event],
)
# --8<-- [end:event_processor]
