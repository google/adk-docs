# Human-in-the-Loop (HITL) with A2A

In many real-world scenarios, an agent may need to pause its work and ask for
human approval before proceeding. While the A2A protocol does not have a
specific concept of "Human-in-the-Loop", it provides the necessary building
blocks to implement this pattern.

This guide explains how to implement a HITL workflow using ADK and the A2A
protocol.

## The Core Concept: The `LongRunningFunctionTool`

The key to this workflow is the `LongRunningFunctionTool`. Unlike a regular
tool that returns a final answer, a long-running tool can return an
intermediate **pending** status. This allows the agent to handle asynchronous
tasks that depend on external input without blocking its own execution.

### The Scenario: An Expense Reimbursement Agent

We will build a system for processing employee expense reports:

- A `root_agent` receives reimbursement requests. If the amount is small, it
  approves it automatically. If it's large, it delegates to a remote
  `approval_agent`.
- The remote `approval_agent` is responsible for the approval workflow. It uses
  a `LongRunningFunctionTool` to formally request a human's decision,
  returning a `pending` status to the `root_agent`.

### The HITL Flow

1.  The `root_agent` calls the remote `approval_agent`.
2.  The remote agent's `LongRunningFunctionTool` immediately returns a response
    with `status: "pending"` and a unique ticket ID.
3.  The `root_agent` receives this pending status and informs the user to wait
    for manager approval.
4.  A human manager interacts with the `root_agent` (in a real app, this could
    be via a button in a UI) to approve or reject the request.
5.  The `root_agent` sends an updated tool response back to the remote
    `approval_agent`, referencing the original ticket ID.
6.  The remote agent's `LongRunningFunctionTool` receives the update, completes
    its execution, and returns the final result.

### Example Code

**1. The Remote Approval Agent (`approval_agent/agent.py`)**

This agent uses a `LongRunningFunctionTool` to initiate the approval workflow.

```python
from google.adk.tools import LongRunningFunctionTool
from google.adk import Agent

# In a real app, you would use a database to store ticket status.
# For this example, we'll use a simple dictionary.
pending_requests = {}

def request_approval(ticket_id: str, amount: float, purpose: str):
    """Initiates the approval request and returns a pending status."""
    print(f"Requesting approval for ticket {ticket_id} for ${amount}...")
    pending_requests[ticket_id] = {"amount": amount, "purpose": purpose}


def complete_approval(ticket_id: str, approved: bool, comment: str) -> str:
    """Completes the approval workflow based on human input."""
    if ticket_id not in pending_requests:
        return f"Error: Ticket {ticket_id} not found."
    if approved:
        return f"Ticket {ticket_id} approved. Comment: {comment}"
    else:
        return f"Ticket {ticket_id} rejected. Comment: {comment}"

approval_tool = LongRunningFunctionTool(
    name="approval_request",
    description="Handles expense approvals, asking for human input.",
    start_func=request_approval,
    end_func=complete_approval,
)

root_agent = Agent(name="approval_agent", tools=[approval_tool])
```

**2. The Root Reimbursement Agent (`reimbursement_agent/agent.py`)**

This agent calls the remote approval agent.

```python
from google.adk import Agent
from google.adk.agents import RemoteA2AAgent

approval_agent_tool = RemoteA2AAgent(
    name="approval_agent",
    description="An agent that can handle expense approvals.",
    agent_card="http://localhost:8002/.well-known/agent.json",
)

root_agent = Agent(
    model='gemini-2.0-flash',
    name='reimbursement_agent',
    instruction='''
        You are an expense reimbursement agent.
        If the amount is less than $100, approve it.
        If the amount is $100 or more, use the approval_agent tool.
    ''',
    tools=[approval_agent_tool],
)
```

**3. Simulating the Human Interaction (`manual_approval.py`)**

This script simulates a manager approving a request. It shows how to construct
the final tool response and send it to the `reimbursement_agent`.

```python
import google.generativeai as genai
import os

# --- Acquiring Your API Key ---
# The client requires an API key for authentication. You can get one from:
# 1. Google AI Studio: Visit https://aistudio.google.com/app/apikey
# 2. A Google Cloud Project: Enable the "Vertex AI API" and create an API key.
#    https://console.cloud.google.com/apis/credentials
#
# Set the key as an environment variable for security:
# export GOOGLE_API_KEY="YOUR_API_KEY"

api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set the GOOGLE_API_KEY environment variable.")

client = genai.configure(transport="rest", api_key=api_key)

# 1. Start the conversation
conversation = client.start_chat(agent_name="reimbursement_agent")

# 2. Make the initial request that requires approval
response = conversation.send_message(
    "Can I get reimbursed for a $500 team dinner?"
)
print(f"Agent: {response.text}")

# 3. Extract the ticket_id from the agent's pending response
# The `response.tool_code` contains the structured tool call.

ticket_id = None
if response.tool_code:
    # In a real app, you would use a more robust parsing method.
    # For this example, we find the ticket_id in the tool call string.
    if "ticket_id" in response.tool_code:
        start = response.tool_code.find("ticket_id=") + len("ticket_id=")
        end = response.tool_code.find("\"", start)
        ticket_id = response.tool_code[start:end]

if not ticket_id:
    raise ValueError("Could not extract ticket_id from agent response.")

print(f"--- Extracted Ticket ID: {ticket_id} ---")

# 4. Simulate the manager's decision and send the final tool output
print("-- Simulating manager approval --")
response = conversation.send_message(
    tool_response={
        "tool_name": "approval_agent",
        "output": {
            "ticket_id": ticket_id,
            "approved": True,
            "comment": "Approved by manager.",
        },
    }
)
print(f"Agent: {response.text}")
```

## Next Steps

This pattern is essential for building robust, real-world agents. For other
advanced topics, see the guide on deployment.

- **Continue to the next guide:** [A2A Deployment Patterns](./deployment-patterns.md)
