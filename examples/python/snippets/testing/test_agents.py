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

"""Tests for the "Test agents without a model API" page.

Every code block on docs/testing/index.md is a section of this file, and the
file runs as written: `pytest test_agents.py`. No model API key, no network.
"""

from typing import Any
from typing import AsyncGenerator

import pytest

from google.adk import Context
from google.adk.agents import Agent
from google.adk.events import RequestInput
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.runners import InMemoryRunner
from google.adk.tools import FunctionTool
from google.adk.tools import ToolContext
from google.adk.workflow import node
from google.adk.workflow import START
from google.adk.workflow import Workflow
from google.genai import types

# --8<-- [start:scripted_model]
class ScriptedLlm(BaseLlm):
    """Answers from a fixed script, one response per turn, with no network call."""

    model: str = "scripted-llm"
    script: list[LlmResponse] = []
    requests: list[LlmRequest] = []

    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        del stream
        self.requests.append(llm_request)
        if self.script:
            yield self.script.pop(0)


def call(name: str, **args) -> LlmResponse:
    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part(function_call=types.FunctionCall(name=name, args=args))],
        )
    )


def say(text: str) -> LlmResponse:
    return LlmResponse(
        content=types.Content(role="model", parts=[types.Part(text=text)])
    )
# --8<-- [end:scripted_model]

# --8<-- [start:tool_calls]
def lookup_order(order_id: str) -> dict:
    """Returns the status of one order."""
    return {"order_id": order_id, "status": "shipped"}


def build_agent(tool, script, name="orders_agent") -> Agent:
    return Agent(name=name, model=ScriptedLlm(script=script), tools=[tool])


@pytest.mark.asyncio
async def test_turn_calls_the_expected_tool():
    runner = InMemoryRunner(
        agent=build_agent(
            lookup_order, [call("lookup_order", order_id="A-1"), say("It shipped.")]
        ),
        app_name="test_app",
    )

    events = await runner.run_debug("Where is order A-1?", quiet=True)

    tool_calls = [fc for event in events for fc in event.get_function_calls()]
    assert [fc.name for fc in tool_calls] == ["lookup_order"]
    assert tool_calls[0].args == {"order_id": "A-1"}
    assert events[-1].content.parts[0].text == "It shipped."
# --8<-- [end:tool_calls]

# --8<-- [start:state]
def cancel_order(order_id: str, tool_context: ToolContext) -> dict:
    """Cancels an order and records it in session state."""
    tool_context.state["last_cancelled"] = order_id
    return {"cancelled": order_id}


@pytest.mark.asyncio
async def test_tool_writes_session_state():
    runner = InMemoryRunner(
        agent=build_agent(
            cancel_order, [call("cancel_order", order_id="A-9"), say("Cancelled.")]
        ),
        app_name="test_app",
    )

    await runner.run_debug("Cancel A-9", quiet=True)

    session = await runner.session_service.get_session(
        app_name="test_app", user_id="debug_user_id", session_id="debug_session_id"
    )
    assert session.state["last_cancelled"] == "A-9"
# --8<-- [end:state]

# --8<-- [start:seed_state]
@pytest.mark.asyncio
async def test_turn_reads_seeded_state():
    runner = InMemoryRunner(
        agent=build_agent(
            lookup_order, [call("lookup_order", order_id="A-1"), say("It shipped.")]
        ),
        app_name="test_app",
    )
    await runner.session_service.create_session(
        app_name="test_app",
        user_id="debug_user_id",
        session_id="debug_session_id",
        state={"pending_action": "delete_file"},
    )

    await runner.run_debug("Where is order A-1?", quiet=True)

    session = await runner.session_service.get_session(
        app_name="test_app", user_id="debug_user_id", session_id="debug_session_id"
    )
    assert "pending_action" in session.state
# --8<-- [end:seed_state]

# --8<-- [start:model_request]
@pytest.mark.asyncio
async def test_model_sees_the_tool_result():
    model = ScriptedLlm(
        script=[call("lookup_order", order_id="A-1"), say("It shipped.")]
    )
    agent = Agent(name="orders_agent", model=model, tools=[lookup_order])
    runner = InMemoryRunner(agent=agent, app_name="test_app")

    await runner.run_debug("Where is order A-1?", quiet=True)

    second_request = model.requests[1]
    sent_back = [
        part.function_response.response
        for content in second_request.contents
        for part in content.parts or []
        if part.function_response
    ]
    assert sent_back == [{"order_id": "A-1", "status": "shipped"}]
# --8<-- [end:model_request]

# --8<-- [start:tool_errors]
def delete_file(path: str) -> dict:
    """Deletes a file."""
    raise PermissionError(f"cannot delete {path}")


@pytest.mark.asyncio
async def test_tool_error_propagates():
    runner = InMemoryRunner(
        agent=build_agent(delete_file, [call("delete_file", path="/etc/hosts")]),
        app_name="test_app",
    )

    with pytest.raises(PermissionError, match="cannot delete /etc/hosts"):
        await runner.run_debug("Delete /etc/hosts", quiet=True)
# --8<-- [end:tool_errors]

# --8<-- [start:artifacts]
async def save_note(note: str, tool_context: ToolContext) -> dict:
    """Saves a note as an artifact."""
    await tool_context.save_artifact(
        "note.txt",
        types.Part(inline_data=types.Blob(mime_type="text/plain", data=note.encode())),
    )
    return {"saved": "note.txt"}


@pytest.mark.asyncio
async def test_tool_saves_an_artifact():
    runner = InMemoryRunner(
        agent=build_agent(
            save_note, [call("save_note", note="hello"), say("Saved it.")]
        ),
        app_name="test_app",
    )

    await runner.run_debug("Save a note that says hello", quiet=True)

    artifact = await runner.artifact_service.load_artifact(
        app_name="test_app",
        user_id="debug_user_id",
        session_id="debug_session_id",
        filename="note.txt",
    )
    assert artifact.inline_data.data == b"hello"
# --8<-- [end:artifacts]

# --8<-- [start:confirmation]
@pytest.mark.asyncio
async def test_paused_run_reports_the_pending_confirmation():
    runner = InMemoryRunner(
        agent=build_agent(
            FunctionTool(delete_file, require_confirmation=True),
            [call("delete_file", path="/etc/hosts")],
        ),
        app_name="test_app",
    )

    events = await runner.run_debug("Delete /etc/hosts", quiet=True)

    pending = [
        confirmation_id
        for event in events
        for confirmation_id in (
            event.actions.requested_tool_confirmations if event.actions else {}
        )
    ]
    answers = [
        response.response
        for event in events
        for response in event.get_function_responses()
    ]
    assert pending
    assert answers == [
        {"error": "This tool call requires confirmation, please approve or reject."}
    ]
# --8<-- [end:confirmation]

# --8<-- [start:workflow]
@node(rerun_on_resume=False)
async def ask_for_approval(ctx: Context, node_input: Any):
    """Pauses the workflow until a client answers the request."""
    yield RequestInput(interrupt_id="approve-1", message="Approve this refund?")


approval_flow = Workflow(name="approval_flow", edges=[(START, ask_for_approval)])


@pytest.mark.asyncio
async def test_workflow_pauses_for_input():
    runner = InMemoryRunner(agent=approval_flow, app_name="test_app")

    events = await runner.run_debug("start", quiet=True)

    requests = [fc for event in events for fc in event.get_function_calls()]
    assert [(fc.id, fc.name) for fc in requests] == [
        ("approve-1", "adk_request_input")
    ]
    assert requests[0].args["message"] == "Approve this refund?"
# --8<-- [end:workflow]
