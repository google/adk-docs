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

"""This example demonstrates how to wrap a CrewAI tool and use it in the ADK.

This example uses a simplified mock of the Serper tool for demonstration.
"""

from crewai.tools import BaseTool as CrewaiBaseTool
from google.adk.integrations.crewai import CrewaiTool


class SerperDevTool(CrewaiBaseTool):
  """A mock SerperDevTool for demonstration."""
  name: str = "Serper Dev Tool"
  description: str = "Search the internet with Serper"

  def _run(self, search_query: str) -> str:
    """Mock run method that returns a fake search result."""
    return f"This is a mock search result for the query: {search_query}"


# Create an instance of the CrewAI tool
crewai_serper_tool = SerperDevTool()

# Wrap the CrewAI tool with the ADK CrewaiTool wrapper
adk_wrapped_tool = CrewaiTool(
    tool=crewai_serper_tool,
    name="internet_search",
    description="Search the internet for the given query.",
)

# Now, `adk_wrapped_tool` can be used in an ADK Agent as any other tool.
