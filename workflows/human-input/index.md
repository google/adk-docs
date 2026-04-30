# Human input for agent workflows

Supported in ADKPython v2.0.0Beta

Being able to request human input for data input, decision verification, or action permission is an important part of many agent-powered workflows. Graph-based workflows in ADK can include human in the loop (HITL) nodes specifically built for obtaining input from humans as part of a workflow. These nodes do not require artificial intelligence (AI) models to run, which can make the input process more predictable and reliable.

Beta Release

ADK 2.0 is a Beta release and may cause breaking changes when used with prior versions of ADK. Do not use ADK 2.0 if you require backwards compatibility, such as in production environments. We encourage you to test this release and we welcome your [feedback](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=v2)!

## Get started

You can implement a human input node in a graph using the ***RequestInput*** class and a text prompt for the user. The following code example shows how to add a human input node to an Workflow graph:

```python
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
```

In this code example, `step1` pauses the execution of the agent until the system receives an input from a user. Once the system receives input from the user, that input is passed to the next node.

## Configuration options

Human input nodes can use the ***RequestInput*** class with the following configuration options:

- **`message`:** Text provided to the user to explain the human input request.
- **`payload`:** Structured data to be used as part of the human input request.
- **`response_schema`:** A data structure the human response must conform to.

Note: Response schema input limitations

For the **response_schema** setting, the ***RequestInput*** class does not automatically reformat human responses to fit a specified data structure. The human response must be provided in the specified format. For a better user experience, consider providing a user interface to collect structured data or use an Agent node to conform unstructured data to the format required.

## Human input examples

The following code examples demonstrate more detailed human input requests, including the use of ***message***, ***payload*** and ***response schema*** parameters.

### Request input with response schema

The following code sample shows how to construct a ***RequestInput*** object in a workflow node, including a ***response schema***:

```python
async def initial_prompt(ctx: Context):
   """Ask the user for itinerary information"""
   input_message = """
       This is an interactive concierge workflow tasked with making you a great
       itinerary for you in your city of choice. If you give some details about
       yourself or what you are generally looking for I can better personalize
       your itinerary.
       For example, input your:
           City (Required),
           Age,
           Hobby,
           Example of attraction you liked
   """
   yield RequestInput(message=input_message, response_schema=str)
```

### Request input with data payload

The following code sample shows how to construct a ***RequestInput*** object in a workflow node, including a ***payload*** and ***response schema***. In this example, the `ActivitiesList` is expected to be completed by an agent node that composes a list of activities, and the `get_user_feedback()` node requests feedback for the user.

```python
class ActivitiesList(BaseModel):
   """Itinerary should be a list of dictionaries for each activity. Each
   activity has a name and a description"""
   itinerary: List[Dict[str, str]]

class UserFeedback(BaseModel):
   """Expected response structure from the user."""
   user_response: str

async def get_user_feedback(node_input: ActivitiesList):
   """
   Retrieves the user's thoughts on the agents initial itinerary in order to
   either expand on, change the list, or exit the loop
   """
   message = (
       f"""
       Here is your recommended base itinerary:\n{node_input}\n\n
       Which of these items appeal to you (if any)?
       """
   )

   yield RequestInput(
       message=message,
       payload=node_input,
        response_schema=UserFeedback,
   )
```
