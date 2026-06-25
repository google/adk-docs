# Human input for agent workflows

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v2.0.0</span><span class="lst-go">Go v2.0.0</span>
</div>

Being able to request human input for data input, decision verification, or
action permission is an important part of many agent-powered workflows.
Graph-based workflows in ADK can include human in the loop (HITL) nodes
specifically built for obtaining input from humans as part of a workflow. These
nodes do not require artificial intelligence (AI) models to run, which can make
the input process more predictable and reliable.

## Get started

=== "Python"

    You can implement a human input node in a graph using the ***RequestInput***
    class and a text prompt for the user. The following code example shows how to
    add a human input node to a Workflow graph:

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

    In this code example, `step1` pauses the execution of the agent until the
    system receives an input from a user. Once the system receives input from the
    user, that input is passed to the next node.

=== "Go"

    In ADK Go, human-in-the-loop (HITL) input is obtained through the
    **tool-confirmation** mechanism rather than graph-based `RequestInput` nodes.
    A tool signals that it needs human approval by setting
    `RequireConfirmation: true` in `functiontool.Config`. The framework
    automatically emits an `adk_request_confirmation` `FunctionCall` event to
    the client. The client displays the confirmation prompt and sends back a
    `FunctionResponse` with `"confirmed": true` or `"confirmed": false`.

    ```go
    --8<-- "examples/go/snippets/graphs/human-input/main.go:simple-hitl"
    ```

## Configuration options

=== "Python"

    Human input nodes can use the ***RequestInput*** class with the following
    configuration options:

    -   **`message`:** Text provided to the user to explain the human input
        request.
    -   **`payload`:** Structured data to be used as part of the human input
        request.
    -   **`response_schema`:** A data structure the human response must conform to.

    !!! note "Note: Response schema input limitations"

        For the **response_schema** setting, the ***RequestInput*** class does not
        automatically reformat human responses to fit a specified data structure. The
        human response must be provided in the specified format. For a better user
        experience, consider providing a user interface to collect structured data
        or use an Agent node to conform unstructured data to the format required.

=== "Go"

    In ADK Go, the HITL tool-confirmation flow is configured through
    `functiontool.Config` and the `agent.ToolContext` interface. The equivalent
    configuration options are:

    -   **`RequireConfirmation`** (`bool` in `functiontool.Config`): Set to
        `true` to make the framework always pause and ask for user approval
        before executing the tool. Equivalent to Python's `message` parameter.
    -   **`hint`** (argument to `ctx.RequestConfirmation`): A human-readable
        string explaining why approval is needed, displayed to the user in the
        confirmation prompt.
    -   **`payload`** (argument to `ctx.RequestConfirmation`): Any structured
        data to include alongside the confirmation request, allowing the client
        to render additional context for the user.

    The client receives the `adk_request_confirmation` `FunctionCall` event and
    must respond with a `FunctionResponse` whose body includes
    `"confirmed": true` or `"confirmed": false`. After the response is received,
    the framework re-invokes the tool function with `ctx.ToolConfirmation()`
    returning the user's decision.

    !!! note "Note: Structured response from the client"

        ADK Go does not automatically parse or validate the structure of the
        user's response payload. If your tool needs structured feedback (for
        example, a selection from a list), include a UI or an agent node to
        collect and validate that data before passing it back as the
        `FunctionResponse` payload.

## Human input examples

The following code examples demonstrate more detailed human input requests.

### Request input with a hint message

=== "Python"

    The following code sample shows how to construct a ***RequestInput*** object
    in a workflow node, including a ***response schema***:

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

=== "Go"

    The following code sample shows how to call `ctx.RequestConfirmation` inside
    a tool function with a descriptive hint. The tool checks
    `ctx.ToolConfirmation()` first; if no confirmation has arrived yet it
    emits the pause request, otherwise it acts on the user's decision:

    ```go
    --8<-- "examples/go/snippets/graphs/human-input/main.go:hitl-with-hint"
    ```

### Request input with a data payload

=== "Python"

    The following code sample shows how to construct a ***RequestInput*** object
    in a workflow node, including a ***payload*** and ***response schema***. In
    this example, the `ActivitiesList` is expected to be completed by an agent
    node that composes a list of activities, and the `get_user_feedback()` node
    requests feedback from the user.

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

=== "Go"

    The following code sample shows how to pass a structured payload alongside
    the confirmation hint. The payload is sent to the client so it can render
    the full itinerary for the user. The tool reads any structured feedback the
    client includes in the `FunctionResponse` payload after the user responds:

    ```go
    --8<-- "examples/go/snippets/graphs/human-input/main.go:hitl-with-payload"
    ```
