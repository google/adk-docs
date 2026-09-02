async def init_state_node(attempts: int = 0):
  yield Event(
      state={
          "attempts": attempts,
      },
  )

async def task_attempt_node(node_input: Content, attempts: int):
  yield Event(
      state={
          "attempts": attempts + 1,
      },
  )

async def read_state_node(ctx: Context):
  print(f"attempts state: {ctx.state}") # attempts state: attempts: 1

root_agent = Workflow(
    name="root_agent",
    edges=[("START", init_state_node, task_attempt_node, read_state_node)],
)