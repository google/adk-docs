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

import os
from google.adk.agents import Agent
from google.adk.tools import google_search  # Import the tool

root_agent = Agent(
   # A unique name for the agent.
   name="google_search_agent",
   # The Large Language Model (LLM) that agent will use.
   model=os.getenv("DEMO_AGENT_MODEL"),
   # A short description of the agent's purpose.
   description="Agent to answer questions using Google Search.",
   # Instructions to set the agent's behavior.
   instruction="Answer the question using the Google Search tool.",
   # Add google_search tool to perform grounding with Google search.
   tools=[google_search],
)
