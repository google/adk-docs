---
description: Learn how to migrate existing AI agents, custom agent loops, and workflows to Google Agent Development Kit (ADK) using Agents CLI and your coding assistant.
---

# Migrate existing agents to ADK

This guide shows you how to migrate an existing agent codebase to Agent Development Kit (ADK) using Agents CLI and your coding agent. Migrating to ADK lets you standardize your agent architecture across multiple languages, use built-in evaluation tools, and deploy directly to Google Cloud.

## Migrate with Agents CLI

Instead of manually rewriting state objects, node graphs, and execution loops line by line, you can use Agents CLI to plan and execute the migration with your coding agent.

Agents CLI installs ADK development skills into coding agents such as Antigravity, Claude Code, Cursor, and Codex. When you open your coding agent in an existing project, it can:

* Analyze your current agent structure, tools, state, and routing rules.
* Map existing components to native ADK classes and graph workflows.
* Propose architecture options with trade-offs.
* Convert tools, agent definitions, and session handling incrementally.
* Generate evaluation datasets to verify behavior before and after migration.

For more information on using the CLI, see the [Agents CLI](https://google.github.io/agents-cli/) documentation.

## Prerequisites

Before starting your migration, make sure you have the following installed:

* Python 3.11 or later
* The [`uv`](https://docs.astral.sh/uv/getting-started/installation/) package manager
* A supported coding agent

Install Agents CLI and its ADK skills into your coding agent:

```bash
uvx google-agents-cli setup
```

To verify the installation:

```bash
agents-cli info
```

## Migration workflow

Follow this process to migrate an existing agent to ADK:

1. [Open your coding agent in the existing project](#open-your-coding-agent-in-the-existing-project)
2. [Brainstorm the migration plan](#brainstorm-the-migration-plan)
3. [Map agent patterns to ADK](#map-agent-patterns-to-adk)
4. [Convert code with evaluation in the loop](#convert-code-with-evaluation-in-the-loop)
5. [Verify and grade with agents-cli](#verify-and-grade-with-agents-cli)

### Open your coding agent in the existing project

Open your terminal or IDE in the root directory of your existing agent project, and start your coding agent. Confirm that the agent detects the ADK skills installed by Agents CLI.

### Brainstorm the migration plan

Ask your coding agent to inspect your current codebase and brainstorm the target ADK architecture. Because the agent has ADK skills loaded, it understands ADK state management, graph workflows, and orchestration patterns.

Use a prompt like this:

```text
I want to migrate this existing agent codebase to Google Agent Development Kit (ADK).
Please inspect our current files, state schema, tools, and control flow.
Propose 2-3 target ADK architecture options with trade-offs, and recommend the cleanest approach.
Include an evaluation plan to verify behavior using agents-cli eval.
```

Your coding agent will analyze:

* **Execution flow:** Single tool-calling loop, deterministic graph workflow, dynamic router, or multi-agent team.
* **Tools:** Functions, parameter signatures, docstrings, and external API calls.
* **Memory and retrieval:** Knowledge stores, vector search integrations, or conversational memory.
* **State:** Variables tracked across turns, scratchpad keys, and session storage.
* **Target classes:** Which ADK classes, such as `Agent` or `Workflow`, fit best.
* **Evaluation strategy:** How to convert existing test cases into evaluation datasets to benchmark the migrated agent.

Once you review the proposed approaches, approve the architecture that matches your requirements.

### Map agent patterns to ADK

ADK replaces custom dispatch loops and state handlers with declarative classes and graph workflows. Use the following mapping as a guide during migration:

| Existing pattern | ADK equivalent | Description |
| :--- | :--- | :--- |
| Custom tool schemas or wrappers | Native Python functions or `FunctionTool` | Plain Python functions with type hints and docstrings. ADK automatically derives tool declarations. |
| Custom agent loops or runners | `Agent` | Declarative agent definition specifying model, instructions, tools, and sub-agents. |
| Memory and retrieval | `BaseMemoryService` implementations and retrieval tools | Built-in memory services (`InMemoryMemoryService`, `VertexAiMemoryBankService`, `VertexAiRagMemoryService`) plus retrieval tools for session and document grounding. |
| State dictionaries or scratchpads | `session.state` via `ToolContext` | Shared, mutable session state accessible inside tools, callbacks, and agent instructions. |
| Multi-agent workflows and pipelines | `google.adk.workflow.Workflow` | Explicit graph nodes with conditional routes, loops, and parallel branching. |
| Multi-agent handoffs | `Agent(sub_agents=[...])` | Hierarchical delegation where a coordinator agent delegates to specialized sub-agents. |
| Remote agent communication | A2A Protocol | Inter-agent communication over HTTP using the Agent-to-Agent standard. |

### Convert code with evaluation in the loop

A reliable migration is test-driven. Your coding agent can set up evaluation datasets and test suites alongside the new ADK code to verify that the migrated agent produces the same outcomes as your original implementation.

1. **Set up evaluation test cases:** Have your coding agent convert existing test cases or recorded conversations into evaluation cases under `eval/`.
2. **Port tools and agent logic:** Replace custom dispatch loops and tool wrappers with typed Python functions and an ADK `Agent` or `Workflow`.

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

### Verify and grade with agents-cli

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
* Explore [Graph workflows](/graphs/) for multi-agent routing and state coordination.
* Deploy your agent using the [Deployment guide](/deploy/).
