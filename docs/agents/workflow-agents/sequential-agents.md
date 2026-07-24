# Sequential template workflow agent

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">Typescript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

The ***SequentialAgent*** class is a [template workflow](/agents/workflow-agents/)
agent that executes its sub-agents in the order they are specified in a list.
Use ***SequentialAgent*** when you want execution to occur in a fixed, strict
order. As with other templated workflows, the execution of a
***SequentialAgent*** object is not controlled by an AI model, and is
deterministic in how it executes its sub-agents. The sub-agents specified in the
sequential execution set may or may not utilize AI models, but the overall
execution of those sub-agents is ultimately managed by the ***SequentialAgent***
object you define.

!!! note "Alternative: graph-based workflows"

    Starting in ADK 2.0 for Python and Go, templated workflows have been superseded

    by more flexible workflow structures, including
    [graph-based workflows](/graphs/) and
    [dynamic workflows](/graphs/dynamic/).

### Example scenario

You want to build an agent that can summarize any webpage, using two tools:
**Get Page Contents** and **Summarize Page**. Since the agent must always call
**Get Page Contents** before calling **Summarize Page**, you can build your
agent using the ***SequentialAgent*** class.

### How it works

When the `SequentialAgent`'s `Run Async` method is called, it performs the following actions:

1. **Iteration:** It iterates through the sub agents list in the order they were provided.
2. **Sub-Agent Execution:** For each sub-agent in the list, it calls the sub-agent's `Run Async` method.

![Sequential Agent](/assets/sequential-agent.png){: width="600"}

!!! note "Shared Invocation Context"
    The `SequentialAgent` passes the same `InvocationContext` to each of its
    sub-agents. This means they all share the same session state, including the
    temporary (`temp:`) namespace, making it easy to pass data between steps within
    a single turn.

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
* **Code Refactorer Agent:** An LLM Agent that takes the reviewed code, and the reviewer's comments, and refactors it to improve quality and address issues.

Using a `SequentialAgent` makes it simple to define this exection flow, as shown
in the following code snippet:

```py
SequentialAgent(sub_agents=[CodeWriterAgent, CodeReviewerAgent, CodeRefactorerAgent])
```

This ensures the code is written, *then* reviewed, and *finally* refactored, in a strict, dependable order. **The output from each sub-agent is passed to the next by storing them in state via [Output Key](/agents/llm-agents/##data-handling)**.

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
