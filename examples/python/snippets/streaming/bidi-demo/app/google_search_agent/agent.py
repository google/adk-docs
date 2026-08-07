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

"""Google Search Agent definition for ADK Gemini Live API Toolkit demo."""

import os

from google.adk.agents import Agent
from google.adk.tools import google_search

# Live API models with native audio support:
# - Gemini Live API: gemini-2.5-flash-native-audio-preview-12-2025
#   The default here. Supports proactivity and affective dialog, which this
#   demo exposes as options.
# - Gemini Live API: gemini-3.1-flash-live-preview
#   Newer and lower latency, but supports neither proactivity nor affective
#   dialog.
# - Gemini Live API (Agent Platform): gemini-live-2.5-flash-native-audio
#   GA, and the only Live API model on Agent Platform. Not available in the
#   `global` location.
agent = Agent(
    name="google_search_agent",
    model=os.getenv(
        "DEMO_AGENT_MODEL", "gemini-2.5-flash-native-audio-preview-12-2025"
    ),
    tools=[google_search],
    instruction="You are a helpful assistant that can search the web.",
)
