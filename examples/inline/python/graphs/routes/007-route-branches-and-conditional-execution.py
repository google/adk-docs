from google.adk import Event, Workflow
from google.adk.agents import Agent


def router(node_input: str):
    """Route to task B or C based on node_input."""
    if condition(node_input):
        return Event(route="RUN_TASK_C")
    return Event(route="RUN_TASK_B")

task_B_node = Agent(name="task_B_agent") # An agent to execute node B

def task_C_node(node_input: str):
    """A FunctionNode to execute node C."""
    return Event(output="Task C completed")

root_agent = Workflow(
    name="routing_workflow",
    edges=[
        ("START", task_A_node, router),
        (router,
          {
            # "route value": node_to_run
            "RUN_TASK_B": task_B_node,
            "RUN_TASK_C": task_C_node,
          },
        ),
    ],
)