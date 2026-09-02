---
description: Learn how to migrate existing AI agents, custom agent loops, and workflows to Google Agent Development Kit (ADK) using Agents CLI and your coding assistant.
---

# Migrate existing agents to ADK

This guide shows you how to migrate an existing agent codebase to Agent Development Kit (ADK) using Agents CLI and your coding assistant.

Instead of manually rewriting state objects, node graphs, and execution loops line by line, you can use Agents CLI to plan and execute the migration with your coding assistant.

## Why migrate with Agents CLI

Agents CLI installs ADK development skills into coding assistants such as Antigravity, Claude Code, Cursor, and Codex. When you open your coding assistant in an existing project, it can:

* Analyze your current agent structure, tools, state, and routing rules.
* Map existing components to native ADK classes and functions.
* Propose architecture options with trade-offs.
* Convert tools, agent definitions, and session handling incrementally.
* Generate evaluation datasets to verify behavior before and after migration.

## Prerequisites

Before starting your migration, make sure you have the following installed:

* Python 3.11 or later
* The [`uv`](https://docs.astral.sh/uv/getting-started/installation/) package manager
* A supported coding assistant, such as Antigravity, Claude Code, Cursor, Codex, or Pi

Install Agents CLI and its ADK skills across your coding assistants:

```bash
uvx google-agents-cli setup
```

To verify the installation:

```bash
agents-cli info
```

## Migration workflow

Follow this step-by-step process to migrate an existing agent to ADK.

```
Existing Agent Codebase
         │
         ▼
Step 1: Open coding agent in project
         │
         ▼
Step 2: Brainstorm migration architecture
         │
         ▼
Step 3: Map agent patterns to ADK
         │
         ▼
Step 4: Test-driven conversion
         │
         ▼
Step 5: Verify and grade with agents-cli eval
```

### Step 1: Open your coding agent in the existing project

Open your terminal or IDE in the root directory of your existing agent project, and start your coding assistant, such as Antigravity, Claude Code, Cursor, Codex, or VS Code. Confirm that the assistant detects the ADK skills installed by Agents CLI.

### Step 2: Brainstorm the migration plan

Ask your coding assistant to inspect your current codebase and brainstorm the target ADK architecture. Because the assistant has ADK skills loaded, it understands ADK state management and orchestration patterns.

Use a prompt like this:

```text
I want to migrate this existing agent codebase to Google Agent Development Kit (ADK).
Please inspect our current files, state schema, tools, and control flow.
Propose 2-3 target ADK architecture options with trade-offs, and recommend the cleanest approach.
Include an evaluation plan to verify behavior using agents-cli eval.
```

Your coding assistant will analyze:

* **Execution flow:** Single tool-calling loop, deterministic state machine, sequential pipeline, or multi-agent team.
* **Tools:** Functions, parameter signatures, docstrings, and external API calls.
* **State:** Variables tracked across turns, scratchpad keys, and session storage.
* **Target classes:** Which ADK classes, such as `Agent`, `SequentialAgent`, `LoopAgent`, `ParallelAgent`, or `Workflow`, fit best.
* **Evaluation strategy:** How to convert existing test cases into evaluation datasets to benchmark the migrated agent.

Once you review the proposed approaches, approve the architecture that matches your requirements.

### Step 3: Map existing agent patterns to ADK

ADK replaces custom dispatch loops and state handlers with declarative classes. Use the following mapping as a guide during migration:

| Existing pattern | ADK equivalent | Description |
| :--- | :--- | :--- |
| Custom tool schemas or wrappers | Native Python functions or `FunctionTool` | Plain Python functions with type hints and docstrings. ADK automatically derives tool declarations. |
| Custom agent loops or runners | `Agent` | Declarative agent definition specifying model, instructions, tools, and sub-agents. |
| State dictionaries or scratchpads | `session.state` via `ToolContext` | Shared, type-safe session state accessible inside tools, callbacks, and agent instructions. |
| Linear pipeline orchestration | `SequentialAgent` | Executes a sequence of sub-agents in order, passing context downstream. |
| Iterative refinement loops | `LoopAgent` | Runs sub-agents in a loop until an exit condition or max iterations is met. |
| Parallel branching and fan-out | `ParallelAgent` | Executes multiple sub-agents concurrently and aggregates their results. |
| Deterministic state-graph routing | `google.adk.workflow.Workflow` | Explicit graph nodes with conditional event edges for strict routing pipelines. |
| Multi-agent handoffs | `Agent(sub_agents=[...])` | Hierarchical delegation where a coordinator agent delegates to specialized sub-agents. |
| Remote agent communication | A2A Protocol | Inter-agent communication over HTTP using the Agent-to-Agent standard. |
| Memory and retrieval | `MemoryService` and RAG plugins | Built-in memory services and retrieval plugins for session and document grounding. |

### Step 4: Convert code with evaluation in the loop

A reliable migration is test-driven. Your coding assistant can set up evaluation datasets and test suites alongside the new ADK code to verify that the migrated agent produces the same outcomes as your original implementation.

1. **Set up evaluation test cases:** Have your coding assistant convert existing test cases or recorded conversations into evaluation cases under `eval/`.
2. **Port tools and agent logic:** Replace custom dispatch loops and tool wrappers with typed Python functions and an ADK `Agent`.

```python
# agent.py
from google.adk.agents import Agent
from google.adk.tools import ToolContext

def lookup_customer(customer_id: str) -> str:
    """Retrieve account tier and status for a customer."""
    return "Tier: Premium, Status: Active"

def calculate_discount(amount: float, rate: float = 0.1) -> float:
    """Calculate discounted total for a transaction."""
    return amount * (1.0 - rate)

root_agent = Agent(
    name="customer_support_agent",
    model="gemini-2.5-flash",
    instruction="Assist customers with account inquiries and discounts using your tools.",
    tools=[lookup_customer, calculate_discount],
)
```

### Step 5: Verify and grade with agents-cli

Run the evaluation suite to compare the migrated agent against your baseline test cases:

```bash
agents-cli eval run
```

You can also test queries directly or interactively:

```bash
# Test a single prompt
agents-cli run "Look up customer cust_101 and apply a 10% discount on $100."

# Start the interactive web UI
agents-cli playground
```

## Next steps

* Read the [Multi-tool agent tutorial](/tutorials/multi-tool-agent/) to learn more about ADK tool patterns.
* Review [Multi-agent workflows](/workflows/) to structure multi-agent teams.
* Deploy your agent using the [Deployment guide](/deploy/).
