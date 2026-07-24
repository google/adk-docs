# Human input for agent workflows

Supported in ADKPython v2.0.0Go v2.0.0

Being able to request human input for data input, decision verification, or action permission is an important part of many agent-powered workflows. Graph-based workflows in ADK can include human in the loop (HITL) nodes specifically built for obtaining input from humans as part of a workflow. These nodes do not require artificial intelligence (AI) models to run, which can make the input process more predictable and reliable.

## Get started

You can implement a human input node in a graph using the ***RequestInput*** class and a text prompt for the user. The following code example shows how to add a human input node to a Workflow graph:

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

In ADK Go v2.0.0, a HITL graph node is built with `workflow.NewEmittingFunctionNode` and `workflow.ResumeOrRequestInput`. This is the direct equivalent of Python's `RequestInput` node:

- On the **first pass**, `workflow.ResumeOrRequestInput` emits a `session.RequestInput` event (surfaced as `Event.RequestedInput`) and returns `ErrNodeInterrupted`, pausing the workflow.
- After the human replies, the node is **re-invoked from the top** (`RerunOnResume: &true`) and `ResumeOrRequestInput` returns the reply payload, which flows as typed input to the next node via `event.Output`.

```go
// newGraphHITLWorkflow demonstrates a graph HITL node using
// workflow.NewEmittingFunctionNode and workflow.ResumeOrRequestInput.
//
// This is the Go equivalent of the Python RequestInput node:
//
//  def step1():  # Human input step
//      yield RequestInput(message="Enter a number:")
//
//  def step2(node_input):
//      return node_input * 2
//
//  root_agent = Workflow(
//      name="root_agent",
//      edges=[('START', step1, step2)],
//  )
//
// On the first pass, step1Node emits a RequestInput event and pauses the
// workflow (ErrNodeInterrupted). After the human replies, the node is re-run
// and ResumeOrRequestInput returns the reply, which flows as typed input to
// step2Node via event.Output.
func newGraphHITLWorkflow() (agent.Agent, error) {
    rerun := true

    // step1Node: pauses for human input on the first pass, returns the
    // human's reply on resume. workflow.ResumeOrRequestInput handles both
    // phases — no manual re-entry bookkeeping needed.
    step1Node := workflow.NewEmittingFunctionNode[any, string]("step1",
        func(ctx agent.Context, _ any, emit func(*session.Event) error) (string, error) {
            reply, err := workflow.ResumeOrRequestInput(ctx, emit, session.RequestInput{
                InterruptID: "enter_number",
                Message:     "Enter a number:",
            })
            if err != nil {
                // ErrNodeInterrupted on first pass — workflow pauses here.
                return "", err
            }
            // On resume, reply is the human's text response.
            number, _ := reply.(string)
            return number, nil
        },
        workflow.NodeConfig{RerunOnResume: &rerun},
    )

    // step2Node: receives the human's input as its typed string input via
    // event.Output and doubles the number.
    step2Node := workflow.NewFunctionNode("step2",
        func(_ agent.Context, input string) (string, error) {
            return fmt.Sprintf("You entered: %s (doubled: %s%s)", input, input, input), nil
        },
        workflow.NodeConfig{},
    )

    return workflowagent.New(workflowagent.Config{
        Name:        "root_agent",
        Description: "Pauses for a number from the user, then doubles it.",
        Edges:       workflow.Chain(workflow.Start, step1Node, step2Node),
    })
}
```

## Configuration options

Human input nodes can use the ***RequestInput*** class with the following configuration options:

- **`message`:** Text provided to the user to explain the human input request.
- **`payload`:** Structured data to be used as part of the human input request.
- **`response_schema`:** A data structure the human response must conform to.

Note: Response schema input limitations

For the **response_schema** setting, the ***RequestInput*** class does not automatically reformat human responses to fit a specified data structure. The human response must be provided in the specified format. For a better user experience, consider providing a user interface to collect structured data or use an Agent node to conform unstructured data to the format required.

`session.RequestInput` carries the following fields, which map directly to Python's `RequestInput` parameters:

- **`InterruptID`** (`string`): A unique identifier for this pause point. Use a stable prefix plus a UUID to avoid collision across workflow runs. Equivalent to the implicit interrupt ID in Python.
- **`Message`** (`string`): Human-readable prompt displayed to the user. Equivalent to Python's `message` parameter.
- **`Payload`** (`any`): Optional structured data sent alongside the prompt so the client can render additional context. Equivalent to Python's `payload` parameter.

`workflow.NodeConfig.RerunOnResume` controls what happens on resume:

- **`&true`**: the node body is re-run from the top; `ResumeOrRequestInput` returns the human's reply on the second pass. Required for nodes that use `ResumeOrRequestInput`.
- **`&false`** or **`nil`** (leaf default): the reply is routed to the node's successor as input, bypassing the interrupted node.

Note: Structured response from the client

ADK Go does not automatically parse or validate the structure of the human's reply payload. If your workflow needs structured feedback, include a UI or a downstream agent node to validate the response before acting on it.

## Human input examples

The following code examples demonstrate more detailed human input requests.

### Request input with a message and payload

The following code sample shows how to construct a ***RequestInput*** object in a workflow node, including a ***payload*** and ***response schema***. In this example, the `ActivitiesList` is expected to be completed by an agent node that composes a list of activities, and the `get_user_feedback()` node requests feedback from the user.

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

The following code sample shows a three-node graph: a builder node generates a structured itinerary, a HITL node sends it as `Payload` alongside the prompt, and a final node acts on the user's feedback. The `Payload` field lets the client render the full itinerary for the user before they respond:

```go
// ItineraryItem represents a single activity in a travel plan.
type ItineraryItem struct {
    Name        string `json:"name"`
    Description string `json:"description"`
}

// newItineraryReviewWorkflow demonstrates a graph HITL node that sends a
// structured payload alongside the input prompt so the client can render
// additional context for the user. This mirrors Python's:
//
//  async def get_user_feedback(node_input: ActivitiesList):
//      yield RequestInput(
//          message="Which items appeal to you?",
//          payload=node_input,
//          response_schema=UserFeedback,
//      )
func newItineraryReviewWorkflow() (agent.Agent, error) {
    rerun := true

    // buildItineraryNode: generates an itinerary and passes it to the HITL
    // node as its typed output via event.Output.
    buildItineraryNode := workflow.NewFunctionNode("build_itinerary",
        func(_ agent.Context, _ any) ([]ItineraryItem, error) {
            return []ItineraryItem{
                {Name: "Eiffel Tower", Description: "Iconic iron lattice tower."},
                {Name: "Louvre Museum", Description: "World's largest art museum."},
                {Name: "Seine River Cruise", Description: "Scenic boat tour of Paris."},
            }, nil
        },
        workflow.NodeConfig{},
    )

    // reviewNode: sends the itinerary as payload alongside the prompt so the
    // client can display it. On resume, the human's selection is returned.
    reviewNode := workflow.NewEmittingFunctionNode[[]ItineraryItem, string]("get_user_feedback",
        func(ctx agent.Context, itinerary []ItineraryItem, emit func(*session.Event) error) (string, error) {
            reply, err := workflow.ResumeOrRequestInput(ctx, emit, session.RequestInput{
                InterruptID: "itinerary_review",
                Message:     fmt.Sprintf("Here is your recommended itinerary (%d activities). Which items appeal to you?", len(itinerary)),
                Payload:     itinerary, // structured payload rendered by the client
            })
            if err != nil {
                // ErrNodeInterrupted on first pass — workflow pauses here.
                return "", err
            }
            feedback, _ := reply.(string)
            return feedback, nil
        },
        workflow.NodeConfig{RerunOnResume: &rerun},
    )

    // finalNode: receives the user's feedback and produces a confirmation.
    finalNode := workflow.NewFunctionNode("finalize",
        func(_ agent.Context, feedback string) (string, error) {
            return fmt.Sprintf("Itinerary finalised with your feedback: %q", feedback), nil
        },
        workflow.NodeConfig{},
    )

    return workflowagent.New(workflowagent.Config{
        Name:        "concierge_workflow",
        Description: "Builds an itinerary, asks the user for feedback, then finalises.",
        Edges:       workflow.Chain(workflow.Start, buildItineraryNode, reviewNode, finalNode),
    })
}
```

## Tool-confirmation: approval prompts in LLM agents

Tool-confirmation is a separate, LLM-agent–level mechanism for yes/no approval prompts. Unlike graph HITL nodes, tool-confirmation works inside an `llmagent` tool function rather than as a standalone graph node. It is useful when you want an LLM agent to pause and ask for approval before executing a specific tool call.

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

Set `RequireConfirmation: true` in `functiontool.Config` for a static yes/no approval before a tool executes, or call `ctx.RequestConfirmation` from inside the tool for a custom hint message:

```go
// DoubleNumberArgs holds the input for the doubleNumber tool.
type DoubleNumberArgs struct {
    Number int `json:"number" jsonschema:"The number to double."`
}

// DoubleNumberResults holds the output of the doubleNumber tool.
type DoubleNumberResults struct {
    Result int `json:"result"`
}

// doubleNumber is a tool that doubles the given number.
// Because RequireConfirmation is true, the framework automatically pauses
// execution and emits an "adk_request_confirmation" event to the client before
// running the tool. The client must reply with a FunctionResponse confirming
// or denying the action.
func doubleNumber(_ agent.Context, args DoubleNumberArgs) (DoubleNumberResults, error) {
    return DoubleNumberResults{Result: args.Number * 2}, nil
}

// newSimpleHITLAgent creates an LLM agent with a tool that always requires
// user confirmation before it executes (tool-confirmation pattern).
func newSimpleHITLAgent(ctx context.Context) (agent.Agent, error) {
    model, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
    if err != nil {
        return nil, fmt.Errorf("failed to create model: %w", err)
    }

    doubleNumberTool, err := functiontool.New(
        functiontool.Config{
            Name:                "double_number",
            Description:         "Doubles the given number. Requires user approval before running.",
            RequireConfirmation: true,
        },
        doubleNumber,
    )
    if err != nil {
        return nil, fmt.Errorf("failed to create tool: %w", err)
    }

    return llmagent.New(llmagent.Config{
        Name:        "double_number_agent",
        Model:       model,
        Instruction: "You are a helpful assistant. When asked to double a number, use the double_number tool.",
        Tools:       []tool.Tool{doubleNumberTool},
    })
}
```

For a custom hint with manual re-entry handling:

```go
// BookFlightArgs holds the input for the bookFlight tool.
type BookFlightArgs struct {
    Origin      string `json:"origin"      jsonschema:"Departure airport code."`
    Destination string `json:"destination" jsonschema:"Arrival airport code."`
    Date        string `json:"date"        jsonschema:"Travel date in YYYY-MM-DD format."`
}

// BookFlightResults holds the outcome of the bookFlight tool.
type BookFlightResults struct {
    Status        string `json:"status"`
    ConfirmNumber string `json:"confirm_number,omitempty"`
}

// bookFlight is a tool that pauses for human approval before completing a
// booking (tool-confirmation pattern with a custom hint message).
func bookFlight(ctx agent.Context, args BookFlightArgs) (BookFlightResults, error) {
    if confirmation := ctx.ToolConfirmation(); confirmation != nil {
        if !confirmation.Confirmed {
            return BookFlightResults{Status: "Booking cancelled by user."}, nil
        }
        return BookFlightResults{
            Status:        "Booking confirmed.",
            ConfirmNumber: "FLT-20251031",
        }, nil
    }

    hint := fmt.Sprintf(
        "The agent wants to book a flight from %s to %s on %s. Do you approve?",
        args.Origin, args.Destination, args.Date,
    )
    if err := ctx.RequestConfirmation(hint, nil); err != nil {
        return BookFlightResults{}, fmt.Errorf("failed to request confirmation: %w", err)
    }
    return BookFlightResults{Status: "Awaiting user approval."}, nil
}

// newHITLWithHintAgent creates an LLM agent whose bookFlight tool manually
// requests confirmation with a descriptive hint (tool-confirmation pattern).
func newHITLWithHintAgent(ctx context.Context) (agent.Agent, error) {
    model, err := gemini.NewModel(ctx, modelName, &genai.ClientConfig{})
    if err != nil {
        return nil, fmt.Errorf("failed to create model: %w", err)
    }

    bookFlightTool, err := functiontool.New(
        functiontool.Config{
            Name:        "book_flight",
            Description: "Books a flight between two airports on a given date.",
        },
        bookFlight,
    )
    if err != nil {
        return nil, fmt.Errorf("failed to create tool: %w", err)
    }

    return llmagent.New(llmagent.Config{
        Name:        "flight_booking_agent",
        Model:       model,
        Instruction: "You are a flight booking assistant. Help the user book flights.",
        Tools:       []tool.Tool{bookFlightTool},
    })
}
```
