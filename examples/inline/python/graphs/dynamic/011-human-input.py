from typing import Any
from google.adk import Context
from google.adk.events import RequestInput
from google.adk.workflow import node


@node(rerun_on_resume=False)
async def get_user_approval(ctx: Context, node_input: Any):
    """Yields a RequestInput to pause the workflow and wait for user input."""
    yield RequestInput(message="Please approve this request (Yes/No)")


@node(rerun_on_resume=True)
async def handle_process(ctx: Context, node_input: Any):
    """The orchestrator calling the interactive step."""
    user_response = await ctx.run_node(get_user_approval)

    if user_response.lower() == "yes":
        return "Approved"
    return "Denied"