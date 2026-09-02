# Multi-agent workflow patterns

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

This guide provides a number of agent patterns which you can implement with
Agent Development Kit (ADK), including code examples. These patterns are useful
across a broad set of applications and you should evaluate and test them against
your project requirements before committing to a full implementation.

## Coordinator and dispatcher

* **Structure:** A central [`LlmAgent`](/agents/llm-agents/) (Coordinator) manages several specialized `sub_agents`.
* **Goal:** Route incoming requests to the appropriate specialist agent.
* **ADK Primitives Used:**
    * **Hierarchy:** Coordinator has specialists listed in `sub_agents`.
    * **Interaction:** Primarily uses **LLM-Driven Delegation** (requires clear `description`s on sub-agents and appropriate `instruction` on Coordinator) or **Explicit Invocation (`AgentTool`)** (Coordinator includes `AgentTool`-wrapped specialists in its `tools`).

=== "Python"

    ```python
    --8<-- "examples/inline/python/workflows/patterns/001-coordinator-and-dispatcher.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/workflows/patterns/002-coordinator-and-dispatcher.ts"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/workflows/patterns/003-coordinator-and-dispatcher.go.txt"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/workflows/patterns/004-coordinator-and-dispatcher.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/agents/multi-agent/MultiAgentExample.kt:coordinator_pattern"
    ```

## Sequential pipeline

* **Structure:** A [`SequentialAgent`](/agents/workflow-agents/sequential-agents/) contains `sub_agents` executed in a fixed order.
* **Goal:** Implement a multistep process where the output of one-step feeds into the next.
* **ADK Primitives Used:**
    * **Workflow:** `SequentialAgent` defines the order.
    * **Communication:** Primarily uses **Shared Session State**. Earlier agents write results (often via `output_key`), later agents read those results from `context.state`.

=== "Python"

    ```python
    --8<-- "examples/inline/python/workflows/patterns/005-sequential-pipeline.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/workflows/patterns/006-sequential-pipeline.ts"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/workflows/patterns/007-sequential-pipeline.go.txt"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/workflows/patterns/008-sequential-pipeline.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/agents/multi-agent/MultiAgentExample.kt:sequential_pipeline_pattern"
    ```

## Parallel fan-out and gather

* **Structure:** A [`ParallelAgent`](/agents/workflow-agents/parallel-agents/) runs multiple `sub_agents` concurrently, often followed by a later agent (in a `SequentialAgent`) that aggregates results.
* **Goal:** Execute independent tasks simultaneously to reduce latency, then combine their outputs.
* **ADK Primitives Used:**
    * **Workflow:** `ParallelAgent` for concurrent execution (Fan-Out). Often nested within a `SequentialAgent` to handle the subsequent aggregation step (Gather).
    * **Communication:** Sub-agents write results to distinct keys in **Shared Session State**. The subsequent "Gather" agent reads multiple state keys.

=== "Python"

    ```python
    --8<-- "examples/inline/python/workflows/patterns/009-parallel-fan-out-and-gather.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/workflows/patterns/010-parallel-fan-out-and-gather.ts"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/workflows/patterns/011-parallel-fan-out-and-gather.go.txt"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/workflows/patterns/012-parallel-fan-out-and-gather.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/agents/multi-agent/MultiAgentExample.kt:parallel_gather_pattern"
    ```

## Hierarchical task decomposition

* **Structure:** A multi-level tree of agents where higher-level agents break down complex goals and delegate sub-tasks to lower-level agents.
* **Goal:** Solve complex problems by recursively breaking them down into simpler, executable steps.
* **ADK Primitives Used:**
    * **Hierarchy:** Multi-level `parent_agent`/`sub_agents` structure.
    * **Interaction:** Primarily **LLM-Driven Delegation** or **Explicit Invocation (`AgentTool`)** used by parent agents to assign tasks to subagents. Results are returned up the hierarchy (via tool responses or state).

=== "Python"

    ```python
    --8<-- "examples/inline/python/workflows/patterns/013-hierarchical-task-decomposition.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/workflows/patterns/014-hierarchical-task-decomposition.ts"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/workflows/patterns/015-hierarchical-task-decomposition.go.txt"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/workflows/patterns/016-hierarchical-task-decomposition.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/agents/multi-agent/MultiAgentExample.kt:hierarchical_pattern"
    ```

## Generate and review pattern

* **Structure:** Typically involves two agents within a [`SequentialAgent`](/agents/workflow-agents/sequential-agents/): a generator agent and a critic reviewer agent.
* **Goal:** Improve the quality or validity of generated output by having a dedicated agent review it.
* **ADK Primitives Used:**
    * **Workflow:** `SequentialAgent` ensures generation happens before review.
    * **Communication:** **Shared Session State** (Generator uses `output_key` to save output; Reviewer reads that state key). The Reviewer might save its feedback to another state key for subsequent steps.

=== "Python"

    ```python
    --8<-- "examples/inline/python/workflows/patterns/017-generate-and-review-pattern.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/workflows/patterns/018-generate-and-review-pattern.ts"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/workflows/patterns/019-generate-and-review-pattern.go.txt"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/workflows/patterns/020-generate-and-review-pattern.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/agents/multi-agent/MultiAgentExample.kt:generator_critic_pattern"
    ```

## Iterative refinement

* **Structure:** Uses a [`LoopAgent`](/agents/workflow-agents/loop-agents/) containing one or more agents that work on a task over multiple iterations.
* **Goal:** Progressively improve a result (e.g., code, text, plan) stored in the session state until a quality threshold is met or a maximum number of iterations is reached.
* **ADK Primitives Used:**
    * **Workflow:** `LoopAgent` manages the repetition.
    * **Communication:** **Shared Session State** is essential for agents to read the previous iteration's output and save the refined version.
    * **Termination:** The loop typically ends based on `max_iterations` or a dedicated checking agent setting `escalate=True` in the `Event Actions` when the result is satisfactory.

=== "Python"

    ```python
    --8<-- "examples/inline/python/workflows/patterns/021-iterative-refinement.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/workflows/patterns/022-iterative-refinement.ts"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/workflows/patterns/023-iterative-refinement.go.txt"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/workflows/patterns/024-iterative-refinement.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/agents/multi-agent/MultiAgentExample.kt:iterative_refinement_pattern"
    ```

## Human-in-the-loop

* **Structure:** Integrates human intervention points within an agent workflow.
* **Goal:** Allow for human oversight, approval, correction, or tasks that AI cannot perform.
* **ADK Primitives Used (Conceptual):**
    * **Interaction:** Can be implemented using a custom **Tool** that pauses execution and sends a request to an external system (e.g., a UI, ticketing system) waiting for human input. The tool then returns the human's response to the agent.
    * **Workflow:** Could use **LLM-Driven Delegation** (`transfer_to_agent`) targeting a conceptual "Human Agent" that triggers the external workflow, or use the custom tool within an `LlmAgent`.
    * **State/Callbacks:** State can hold task details for the human; callbacks can manage the interaction flow.
    * **Note:** ADK doesn't have a built-in "Human Agent" type, so this requires custom integration.

=== "Python"

    ```python
    --8<-- "examples/inline/python/workflows/patterns/025-human-in-the-loop.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/workflows/patterns/026-human-in-the-loop.ts"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/workflows/patterns/027-human-in-the-loop.go.txt"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/workflows/patterns/028-human-in-the-loop.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/agents/multi-agent/MultiAgentExample.kt:human_in_loop_pattern"
    ```

### Human in the loop with Policy

A more advanced and structured way to implement Human-in-the-Loop is by using a `PolicyEngine`. This approach allows you to define policies that can trigger a confirmation step from a user before a tool is executed. The `SecurityPlugin` intercepts a tool call, consults the `PolicyEngine`, and if the policy dictates, it will automatically request user confirmation. This pattern is more robust for enforcing governance and security rules.

Here's how it works:

1.  **`SecurityPlugin`**: You add this plugin to your `Runner`. It acts as an interceptor for all tool calls.
2.  **`BasePolicyEngine`**: You create a custom class that implements this interface. Its `evaluate()` method contains your logic to decide if a tool call needs confirmation.
3.  **`PolicyOutcome.CONFIRM`**: When your `evaluate()` method returns this outcome, the `SecurityPlugin` pauses the tool execution and generates a special `FunctionCall` using `getAskUserConfirmationFunctionCalls`.
4.  **Application Handling**: Your application code receives this special function call and presents the confirmation request to the user.
5.  **User Confirmation**: Once the user confirms, your application sends a `FunctionResponse` back to the agent, which allows the `SecurityPlugin` to proceed with the original tool execution.

!!! Note "TypeScript Recommended Pattern"
    The Policy-based pattern is the recommended approach for implementing Human-in-the-Loop workflows in TypeScript. Support in other ADK languages is planned for future releases.

A conceptual example of using a `CustomPolicyEngine` to require user confirmation before executing any tool is shown below.

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/workflows/patterns/029-human-in-the-loop-with-policy.ts"
    ```

    You can find the full code sample [here](https://github.com/google/adk-docs/blob/main/examples/typescript/snippets/agents/workflow-agents/hitl_confirmation_agent.ts).
