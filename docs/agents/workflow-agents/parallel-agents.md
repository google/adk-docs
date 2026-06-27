# Parallel template workflow agent

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">Typescript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

The ***ParallelAgent*** class is a [template workflow](/agents/workflow-agents/)
agent that executes its sub-agents concurrently. This execution strategy can
dramatically speed up workflows where two or more tasks can be performed
independently. For scenarios prioritizing speed and involving independent,
resource-intensive tasks, this templated workflow facilitates parallel
execution, which can significantly reduce overall processing time. When using
this workflow type, it is important that each sub-agent can operate without
depending on the other sub-agents. This workflow type is particularly beneficial
for operations like multi-source data retrieval or heavy computations, where
parallelization yields substantial performance gains.

As with other templated workflows, the execution of a ***ParallelAgent*** object
is not controlled by an AI model, and is deterministic in how it executes its
sub-agents. The sub-agents specified in the parallel execution set may or may
not utilize AI models, but the overall execution of those sub-agents is
ultimately managed by the ***ParallelAgent*** object you define.

!!! note "Alternative: graph-based workflows"

    Starting in ADK 2.0, templated workflows have been superseded

    by more flexible workflow structures, including
    [graph-based workflows](/workflows/graphs/) and
    [dynamic workflows](/workflows/dynamic/).

### How it works

When the `ParallelAgent`'s `run_async()` method is called:

1. **Concurrent Execution:** It initiates the `run_async()` method of *each* sub-agent present in the `sub_agents` list *concurrently*.  This means all the agents start running at (approximately) the same time.
2. **Independent Branches:**  Each sub-agent operates in its own execution branch.  There is ***no* automatic sharing of conversation history or state between these branches** during execution.
3. **Result Collection:** The `ParallelAgent` manages the parallel execution and, typically, provides a way to access the results from each sub-agent after they have completed (e.g., through a list of results or events). The order of results may not be deterministic.

### Independent Execution and State Management

It's *crucial* to understand that sub-agents within a `ParallelAgent` run independently.  If you *need* communication or data sharing between these agents, you must implement it explicitly.  Possible approaches include:

* **Shared `InvocationContext`:** You could pass a shared `InvocationContext` object to each sub-agent.  This object could act as a shared data store.  However, you'd need to manage concurrent access to this shared context carefully (e.g., using locks) to avoid race conditions.
* **External State Management:**  Use an external database, message queue, or other mechanism to manage shared state and facilitate communication between agents.
* **Post-Processing:** Collect results from each branch, and then implement logic to coordinate data afterwards.

![Parallel Agent](/assets/parallel-agent.png){: width="600"}

### Full Example: Parallel Web Research

Imagine researching multiple topics simultaneously:

1. **Researcher Agent 1:**  An `LlmAgent` that researches "renewable energy sources."
2. **Researcher Agent 2:**  An `LlmAgent` that researches "electric vehicle technology."
3. **Researcher Agent 3:**  An `LlmAgent` that researches "carbon capture methods."

    ```py
    ParallelAgent(sub_agents=[ResearcherAgent1, ResearcherAgent2, ResearcherAgent3])
    ```

These research tasks are independent.  Using a `ParallelAgent` allows them to run concurrently, potentially reducing the total research time significantly compared to running them sequentially. The results from each agent would be collected separately after they finish.

???+ "Full Code"

    === "Python"
        ```py
         --8<-- "examples/python/snippets/agents/workflow-agents/parallel_agent_web_research.py:init"
        ```

    === "Typescript"
        ```typescript
         --8<-- "examples/typescript/snippets/agents/workflow-agents/parallel_agent_web_research.ts:init"
        ```

    === "Go"
        ```go
         --8<-- "examples/go/snippets/agents/workflow-agents/parallel/main.go:init"
        ```

    === "Java"
        ```java
         --8<-- "examples/java/snippets/src/main/java/agents/workflow/ParallelResearchPipeline.java:full_code"
        ```
