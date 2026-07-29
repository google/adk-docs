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

from google.adk import Agent, Event, Workflow
from pydantic import BaseModel, Field

MODEL_NAME = "gemini-flash-latest"


class WeekendBudget(BaseModel):
  budget: float = Field(
      default=None, description="The budget for the weekend in US dollars."
  )


def process_input(node_input: str):
  """Saves the user's raw text into the workflow state."""
  return Event(state={"latest_input": node_input})


extract_budget = Agent(
    name="extract_budget",
    model=MODEL_NAME,
    instruction=(
        "You are a data extraction assistant. Read the user's latest input:"
        " '{latest_input}'. Extract the budget they have for their weekend"
        " plans. If they do not explicitly mention a budget, set it to 100."
    ),
    output_schema=WeekendBudget,
    output_key="weekend_budget",
)


def route_weekend(weekend_budget: WeekendBudget):
  amount = weekend_budget.budget

  if amount < 5:
    yield Event(route="too_low")
  elif amount < 100:
    yield Event(route="cheap_ideas")
  else:
    yield Event(route="fancy_ideas")


def handle_too_low():
  """Fallback route for very low budgets."""
  yield Event(
      message="I'm sorry, but a budget under $5 is too low to plan anything fun!"
  )


value_agent = Agent(
    name="value_agent",
    model=MODEL_NAME,
    instruction=(
        "The user is looking for weekend ideas and has a budget of"
        " ${weekend_budget.budget}. Suggest 2 to 3 fun, cheap ideas they"
        " can do that fit strictly within this budget."
    ),
)


premium_agent = Agent(
    name="premium_agent",
    model=MODEL_NAME,
    instruction=(
        # Changed the variable placeholder here:
        "The user is looking for weekend ideas and has a generous budget of"
        " ${weekend_budget.budget}. Suggest 2 to 3 fancy, premium ideas they"
        " can do that utilize this budget."
    ),
)


root_agent = Workflow(
    name="weekend_planner",
    edges=[
        ("START", process_input, extract_budget, route_weekend),

        (
            route_weekend,
            {
                "too_low": handle_too_low,
                "value_ideas": value_agent,
                "premium_ideas": premium_agent,
            },
        ),
    ],
)
