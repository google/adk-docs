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

    In ADK Go v2.0.0, a HITL graph node is built with
    `workflow.NewEmittingFunctionNode` and `workflow.ResumeOrRequestInput`.
    This is the direct equivalent of Python's `RequestInput` node:

    -   On the **first pass**, `workflow.ResumeOrRequestInput` emits a
        `session.RequestInput` event (surfaced as `Event.RequestedInput`) and
        returns `ErrNodeInterrupted`, pausing the workflow.
    -   After the human replies, the node is **re-invoked from the top**
        (`RerunOnResume: &true`) and `ResumeOrRequestInput` returns the reply
        payload, which flows as typed input to the next node via `event.Output`.

    ```go
    --8<-- "examples/go/snippets/graphs/human-input/main.go:graph-hitl-get-started"
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

    `session.RequestInput` carries the following fields, which map directly to
    Python's `RequestInput` parameters:

    -   **`InterruptID`** (`string`): A unique identifier for this pause point.
        Use a stable prefix plus a UUID to avoid collision across workflow runs.
        Equivalent to the implicit interrupt ID in Python.
    -   **`Message`** (`string`): Human-readable prompt displayed to the user.
        Equivalent to Python's `message` parameter.
    -   **`Payload`** (`any`): Optional structured data sent alongside the
        prompt so the client can render additional context. Equivalent to
        Python's `payload` parameter.

    `workflow.NodeConfig.RerunOnResume` controls what happens on resume:

    -   **`&true`**: the node body is re-run from the top; `ResumeOrRequestInput`
        returns the human's reply on the second pass. Required for nodes that
        use `ResumeOrRequestInput`.
    -   **`&false`** or **`nil`** (leaf default): the reply is routed to the
        node's successor as input, bypassing the interrupted node.

    !!! note "Note: Structured response from the client"

        ADK Go does not automatically parse or validate the structure of the
        human's reply payload. If your workflow needs structured feedback,
        include a UI or a downstream agent node to validate the response before
        acting on it.

## Human input examples

The following code examples demonstrate more detailed human input requests.

### Request input with a message and payload

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

    The following code sample shows a three-node graph: a builder node generates
    a structured itinerary, a HITL node sends it as `Payload` alongside the
    prompt, and a final node acts on the user's feedback. The `Payload` field
    lets the client render the full itinerary for the user before they respond:

    ```go
    --8<-- "examples/go/snippets/graphs/human-input/main.go:graph-hitl-with-payload"
    ```

## Tool-confirmation: approval prompts in LLM agents

Tool-confirmation is a separate, LLM-agent–level mechanism for yes/no
approval prompts. Unlike graph HITL nodes, tool-confirmation works inside an
`llmagent` tool function rather than as a standalone graph node. It is useful
when you want an LLM agent to pause and ask for approval before executing a
specific tool call.

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

    Set `RequireConfirmation: true` in `functiontool.Config` for a static
    yes/no approval before a tool executes, or call `ctx.RequestConfirmation`
    from inside the tool for a custom hint message:

    ```go
    --8<-- "examples/go/snippets/graphs/human-input/main.go:simple-hitl"
    ```

    For a custom hint with manual re-entry handling:

    ```go
    --8<-- "examples/go/snippets/graphs/human-input/main.go:hitl-with-hint"
    ```
