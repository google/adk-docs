from google.adk import Event, Workflow


def router(node_input: str):
    """Route to task B or C based on node_input."""
    if condition(node_input):
        return Event(route="RUN_TASK_C")
    return Event(route="RUN_TASK_B")

root_agent = Workflow(
    name="routing_workflow",
    edges=[
        ("START", task_A_node, router),
        (router,
          {
            "RUN_TASK_B": task_B_node,
            "RUN_TASK_C": task_C_node,
          },
        ),
    ],
)