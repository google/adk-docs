import asyncio
from typing import Any
from google.adk import Context
from google.adk.workflow import BaseNode, node


@node(rerun_on_resume=True)
async def parallel_supervisor(
    ctx: Context, node_input: list[Any], real_node: BaseNode
):
    """Runs a worker node in parallel for each item in the input list."""
    tasks = []
    for item in node_input:
        # ctx.run_node returns a future. Append instead of awaiting immediately.
        tasks.append(ctx.run_node(real_node, item))

    # Collect all results in parallel
    results = await asyncio.gather(*tasks)
    return results