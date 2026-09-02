from google.adk import Context
from google.adk.workflow import node
from pydantic import BaseModel
from typing import Any
import asyncio

class Order(BaseModel):
  order_id: str
  cart_items: list[Product]

@node(rerun_on_resume=True)
async def process_all_orders(ctx: Context, node_input: Any):
  orders = await get_orders()

  process_tasks = []
  for order in orders:
    # Use run_id to provide a custom identifier.
    # Custom run_ids must contain at least one non-numeric character
    # to avoid collision with auto-generated sequential numeric IDs.
    task = ctx.run_node(process_order, order, run_id=f"order-{order.order_id}")
    process_tasks.append(task)

  results = await asyncio.gather(*process_tasks)
  return results