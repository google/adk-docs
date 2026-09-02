from google.adk.events import RequestInput
from google.adk import Workflow

def step1(): # Human input step
  yield RequestInput(message="Enter a number:")

def step2(node_input):
  return node_input * 2

root_agent = Workflow(
    name="root_agent",
    edges=[('START', step1, step2)],
)