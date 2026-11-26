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

"""Code for the "Unit testing" page (docs/evaluate/unit-testing.md).

Every block the page shows is a section of this file, and the file runs as a
test module:

    pip install google-adk pytest pytest-asyncio
    pytest examples/python/snippets/testing/test_agents.py
"""

# --8<-- [start:imports]
from typing import AsyncGenerator

from google.adk.agents import LlmAgent
from google.adk.events.request_input import RequestInput
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.runners import InMemoryRunner
from google.adk.tools.tool_context import ToolContext
from google.adk.workflow import START
from google.adk.workflow import Workflow
from google.genai import types
from pydantic import Field
import pytest
# --8<-- [end:imports]


# --8<-- [start:scripted_model]
class ScriptedModel(BaseLlm):
  """Replies with queued responses and records every request it receives."""

  model: str = "scripted"
  responses: list[types.Content] = Field(default_factory=list)
  requests: list[LlmRequest] = Field(default_factory=list)

  async def generate_content_async(
      self, llm_request: LlmRequest, stream: bool = False
  ) -> AsyncGenerator[LlmResponse, None]:
    self.requests.append(llm_request.model_copy(deep=True))
    yield LlmResponse(content=self.responses.pop(0))


def call(name: str, **args) -> types.Content:
  return types.ModelContent(parts=[types.Part.from_function_call(name=name, args=args)])


def text(value: str) -> types.Content:
  return types.ModelContent(parts=[types.Part.from_text(text=value)])
# --8<-- [end:scripted_model]


# --8<-- [start:tool_calls]
def add_to_cart(item: str, tool_context: ToolContext) -> dict:
  """Adds an item to the cart."""
  cart = tool_context.state.get("cart", []) + [item]
  tool_context.state["cart"] = cart
  return {"cart": cart}


@pytest.mark.asyncio
async def test_agent_adds_item_to_cart():
  model = ScriptedModel(
      responses=[call("add_to_cart", item="apple"), text("Added an apple.")]
  )
  agent = LlmAgent(name="shop", model=model, tools=[add_to_cart])
  runner = InMemoryRunner(agent=agent)

  events = await runner.run_debug("add an apple", quiet=True)

  calls = [fc.name for e in events for fc in e.get_function_calls()]
  assert calls == ["add_to_cart"]
  assert events[-1].content.parts[0].text == "Added an apple."

  session = await runner.session_service.get_session(
      app_name=runner.app_name,
      user_id="debug_user_id",
      session_id="debug_session_id",
  )
  assert session.state["cart"] == ["apple"]
# --8<-- [end:tool_calls]


# --8<-- [start:seed_state]
@pytest.mark.asyncio
async def test_model_sees_state_and_tool_result():
  model = ScriptedModel(
      responses=[call("add_to_cart", item="pear"), text("Done.")]
  )
  agent = LlmAgent(
      name="shop",
      model=model,
      instruction="The customer is on the {plan} plan.",
      tools=[add_to_cart],
  )
  runner = InMemoryRunner(agent=agent)
  await runner.session_service.create_session(
      app_name=runner.app_name,
      user_id="debug_user_id",
      session_id="debug_session_id",
      state={"plan": "premium", "cart": ["apple"]},
  )

  await runner.run_debug("add a pear", quiet=True)

  first, second = model.requests
  assert "The customer is on the premium plan." in first.config.system_instruction
  [response] = [
      part.function_response
      for content in second.contents
      for part in content.parts
      if part.function_response
  ]
  assert response.response == {"cart": ["apple", "pear"]}
# --8<-- [end:seed_state]


# --8<-- [start:tool_errors]
def charge_card(amount: int) -> dict:
  """Charges the card."""
  raise ValueError("card declined")


@pytest.mark.asyncio
async def test_tool_error_reaches_the_test():
  model = ScriptedModel(responses=[call("charge_card", amount=5)])
  agent = LlmAgent(name="pay", model=model, tools=[charge_card])
  runner = InMemoryRunner(agent=agent)

  with pytest.raises(ValueError, match="card declined"):
    await runner.run_debug("pay 5", quiet=True)
# --8<-- [end:tool_errors]


# --8<-- [start:artifacts]
async def save_report(tool_context: ToolContext) -> dict:
  """Saves a report."""
  version = await tool_context.save_artifact(
      "report.txt", types.Part.from_text(text="all good")
  )
  return {"version": version}


@pytest.mark.asyncio
async def test_tool_saves_an_artifact():
  model = ScriptedModel(responses=[call("save_report"), text("Saved.")])
  agent = LlmAgent(name="reporter", model=model, tools=[save_report])
  runner = InMemoryRunner(agent=agent)

  await runner.run_debug("write the report", quiet=True)

  artifact = await runner.artifact_service.load_artifact(
      app_name=runner.app_name,
      user_id="debug_user_id",
      session_id="debug_session_id",
      filename="report.txt",
  )
  assert artifact.text == "all good"
# --8<-- [end:artifacts]


# --8<-- [start:workflow]
@pytest.mark.asyncio
async def test_workflow_resumes_with_the_answer():
  sent = []

  def draft(node_input):
    return "Hello!"

  def approve(node_input):
    return RequestInput(interrupt_id="approve", message=f"Send '{node_input}'?")

  def send(node_input):
    sent.append(node_input)
    return "sent" if node_input["ok"] else "dropped"

  wf = Workflow(name="mailer", edges=[(START, draft, approve, send)])
  runner = InMemoryRunner(node=wf)
  session = await runner.session_service.create_session(
      app_name=runner.app_name, user_id="u"
  )

  async def run(message: types.Content):
    return [
        e
        async for e in runner.run_async(
            user_id="u", session_id=session.id, new_message=message
        )
    ]

  first = await run(types.UserContent("start"))
  [request] = [fc for e in first for fc in e.get_function_calls()]
  assert request.name == "adk_request_input"
  assert request.id == "approve"
  assert sent == []

  answer = types.Content(
      role="user",
      parts=[
          types.Part(
              function_response=types.FunctionResponse(
                  id="approve", name="adk_request_input", response={"ok": True}
              )
          )
      ],
  )
  second = await run(answer)

  assert sent == [{"ok": True}]
  assert [e.output for e in second if e.output is not None][-1] == "sent"
# --8<-- [end:workflow]
