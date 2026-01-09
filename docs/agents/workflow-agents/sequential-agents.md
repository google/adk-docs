# Sequential agents

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">Typescript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

The `SequentialAgent` is a [workflow agent](index.md) that executes its sub-agents in the order they are specified in the list.
Use the `SequentialAgent` when you want the execution to occur in a fixed, strict order.

### Example

* You want to build an agent that can summarize any webpage, using two tools: `Get Page Contents` and `Summarize Page`. Because the agent must always call `Get Page Contents` before calling `Summarize Page` (you can't summarize from nothing!), you should build your agent using a `SequentialAgent`.

As with other [workflow agents](index.md), the `SequentialAgent` is not powered by an LLM, and is thus deterministic in how it executes. That being said, workflow agents are concerned only with their execution (i.e. in sequence), and not their internal logic; the tools or sub-agents of a workflow agent may or may not utilize LLMs.

### How it works

When the `SequentialAgent`'s `Run Async` method is called, it performs the following actions:

1. **Iteration:** It iterates through the sub agents list in the order they were provided.
2. **Sub-Agent Execution:** For each sub-agent in the list, it calls the sub-agent's `Run Async` method.

![Sequential Agent](../../assets/sequential-agent.png){: width="600"}

### Early Exit with `exit_sequence`

The `SequentialAgent` supports early termination when a sub-agent encounters a terminal condition that makes continuing the sequence unnecessary or impossible.

#### When to use early exit:
- **Validation failures:** A validation agent detects critical errors
- **Empty results:** A search agent finds no data to process
- **Blocking conditions:** An agent hits an unrecoverable state
- **Conditional logic:** Based on input analysis, remaining steps aren't needed

#### Usage

Sub-agents can call the `exit_sequence` tool to terminate the sequence early:

```python
from google.adk.tools import exit_sequence

# In your agent's tool function
def validate_input(tool_context: ToolContext):
    if critical_validation_fails:
        exit_sequence(tool_context)  # Stops the sequence here
        return "Validation failed - terminating sequence"
```

#### Example: Search → Analysis → Report Pipeline

```python
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import exit_sequence, google_search

search_agent = LlmAgent(
    name="SearchAgent",
    instruction="Search for results. If no useful results found, call exit_sequence.",
    tools=[google_search, exit_sequence]
)

analysis_agent = LlmAgent(
    name="AnalysisAgent", 
    instruction="Analyze the search results."
)

report_agent = LlmAgent(
    name="ReportAgent",
    instruction="Generate final report."
)

# If search finds no results, analysis and report agents won't execute
pipeline = SequentialAgent(sub_agents=[search_agent, analysis_agent, report_agent])
```

!!! note "Live Mode Support"
    Early exit via `exit_sequence` is supported in both async and live streaming modes. In live mode, the escalate action provides immediate termination, whilst `task_completed()` remains available for natural completion signals.

!!! info "Similar to LoopAgent"
    The `exit_sequence` tool works similarly to [`exit_loop`](loop-agents.md) in LoopAgent, providing a consistent early-exit pattern across workflow agents.

### Full Example: Code Development Pipeline

Consider a simplified code development pipeline:

* **Code Writer Agent:**  An LLM Agent that generates initial code based on a specification.
* **Code Reviewer Agent:**  An LLM Agent that reviews the generated code for errors, style issues, and adherence to best practices.  It receives the output of the Code Writer Agent.
* **Code Refactorer Agent:** An LLM Agent that takes the reviewed code (and the reviewer's comments) and refactors it to improve quality and address issues.

A `SequentialAgent` is perfect for this:

```py
SequentialAgent(sub_agents=[CodeWriterAgent, CodeReviewerAgent, CodeRefactorerAgent])
```

This ensures the code is written, *then* reviewed, and *finally* refactored, in a strict, dependable order. **The output from each sub-agent is passed to the next by storing them in state via [Output Key](../llm-agents.md#structuring-data-input_schema-output_schema-output_key)**.

!!! note "Shared Invocation Context"
    The `SequentialAgent` passes the same `InvocationContext` to each of its sub-agents. This means they all share the same session state, including the temporary (`temp:`) namespace, making it easy to pass data between steps within a single turn.

???+ "Code"

    === "Python"
        ```py
        --8<-- "examples/python/snippets/agents/workflow-agents/sequential_agent_code_development_agent.py:init"
        ```

    === "Typescript"
        ```typescript
        --8<-- "examples/typescript/snippets/agents/workflow-agents/sequential_agent_code_development_agent.ts:init"
        ```

    === "Go"
        ```go
        --8<-- "examples/go/snippets/agents/workflow-agents/sequential/main.go:init"
        ```

    === "Java"
        ```java
        --8<-- "examples/java/snippets/src/main/java/agents/workflow/SequentialAgentExample.java:init"
        ```
