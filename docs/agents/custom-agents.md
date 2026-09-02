# Custom agent template workflows

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

Custom agents and agent-based workflows allow you to define arbitrary
orchestration logic by inheriting directly from `BaseAgent` and implementing
your own control flow. This approach allows you to create new execution patterns
similar to `SequentialAgent`, `LoopAgent`, and `ParallelAgent`, enabling you to
build highly specific and complex agentic workflows.

!!! warning "Alternative: graph-based workflows"

    Starting in ADK 2.0, agent-based workflows using
    `BaseAgent` have been superseded

    by more flexible workflow structures, including
    [graph-based workflows](/workflows/graphs/) and
    [dynamic workflows](/workflows/dynamic/). You should
    evaluate the capabilities of these workflow mechanisms
    ***before*** building a custom agent for your
    target workflow.

!!! warning "Advanced Concept"

    Building custom agents by directly implementing `_run_async_impl`, or its
    equivalent in other languages, provides powerful control but is more complex
    than using the predefined `LlmAgent` or `WorkflowAgent` types. We
    recommend understanding those foundational agent types first before tackling
    custom orchestration logic.

## Overview

A Custom Agent is essentially any class you create that inherits from
`google.adk.agents.BaseAgent` and implements its core execution logic within the
`_run_async_impl` asynchronous method. You have complete control over how this
method calls other sub-agents, manages state, and handles events.

![intro_components.png](/assets/custom-agent-flow.png)

!!! Note

    The specific method name for implementing an agent's core asynchronous logic may
    vary slightly by SDK language, such as `runAsyncImpl` in Java, `_run_async_impl`
    in Python, or `runAsyncImpl` in TypeScript. Refer to the language-specific API
    documentation for details.

### Why build Custom Agents?

After reviewing exising ADK [agent workflow](/workflows/) approaches and architectures,
you may want to consider building a custom workflow agent if those mechanisms cannot
meet one or more of following requirements for your project:

* **Conditional Logic:** Executing different sub-agents or taking different paths based on runtime conditions or the results of previous steps.
* **Complex State Management:** Implementing intricate logic for maintaining and updating state throughout the workflow beyond simple sequential passing.
* **External Integrations:** Incorporating calls to external APIs, databases, or custom libraries directly within the orchestration flow control.
* **Dynamic Agent Selection:** Choosing which sub-agent(s) to run next based on dynamic evaluation of the situation or input.
* **Unique Workflow Patterns:** Implementing orchestration logic that doesn't fit the standard sequential, parallel, or loop structures.

## Implementing custom logic

The core of any custom agent is the method where you define its unique asynchronous behavior. This method allows you to orchestrate sub-agents and manage the flow of execution.

=== "Python"

      The heart of any custom agent is the `_run_async_impl` method. This is where you define its unique behavior.

      * **Signature:** `async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:`
      * **Asynchronous Generator:** It must be an `async def` function and return an `AsyncGenerator`. This allows it to `yield` events produced by sub-agents or its own logic back to the runner.
      * **`ctx` (InvocationContext):** Provides access to crucial runtime information, most importantly `ctx.session.state`, which is the primary way to share data between steps orchestrated by your custom agent.

=== "TypeScript"

    The heart of any custom agent is the `runAsyncImpl` method. This is where you define its unique behavior.

    *   **Signature:** `async* runAsyncImpl(ctx: InvocationContext): AsyncGenerator<Event, void, undefined>`
    *   **Asynchronous Generator:** It must be an `async` generator function (`async*`).
    *   **`ctx` (InvocationContext):** Provides access to crucial runtime information, most importantly `ctx.session.state`, which is the primary way to share data between steps orchestrated by your custom agent.

=== "Go"

    In Go, you implement the `Run` method as part of a struct that satisfies the `agent.Agent` interface. The actual logic is typically a method on your custom agent struct.

    *   **Signature:** `Run(ctx agent.InvocationContext) iter.Seq2[*session.Event, error]`
    *   **Iterator:** The `Run` method returns an iterator (`iter.Seq2`) that yields events and errors. This is the standard way to handle streaming results from an agent's execution.
    *   **`ctx` (InvocationContext):** The `agent.InvocationContext` provides access to the session, including state, and other crucial runtime information.
    *   **Session State:** You can access the session state through `ctx.Session().State()`.

=== "Java"

    The heart of any custom agent is the `runAsyncImpl` method, which you override from `BaseAgent`.

    *   **Signature:** `protected Flowable<Event> runAsyncImpl(InvocationContext ctx)`
    *   **Reactive Stream (`Flowable`):** It must return an `io.reactivex.rxjava3.core.Flowable<Event>`. This `Flowable` represents a stream of events that will be produced by the custom agent's logic, often by combining or transforming multiple `Flowable` from sub-agents.
    *   **`ctx` (InvocationContext):** Provides access to crucial runtime information, most importantly `ctx.session().state()`, which is a `java.util.concurrent.ConcurrentMap<String, Object>`. This is the primary way to share data between steps orchestrated by your custom agent.

### Key capabilities within the core asynchronous method

=== "Python"

    1. **Calling Sub-Agents:** You invoke sub-agents (which are typically stored as instance attributes like `self.my_llm_agent`) using their `run_async` method and yield their events:

          ```python
          --8<-- "examples/inline/python/agents/custom-agents/001-key-capabilities-within-the-core-asynchr.py"
          ```

    2. **Managing State:** Read from and write to the session state dictionary (`ctx.session.state`) to pass data between sub-agent calls or make decisions:

          ```python
          --8<-- "examples/inline/python/agents/custom-agents/002-key-capabilities-within-the-core-asynchr.py"
          ```

    3. **Implementing Control Flow:** Use standard Python constructs (`if`/`elif`/`else`, `for`/`while` loops, `try`/`except`) to create sophisticated, conditional, or iterative workflows involving your sub-agents.

=== "TypeScript"

    1.  **Calling Sub-Agents:** You invoke sub-agents (which are typically stored as instance properties like `this.myLlmAgent`) using their `run` method and yield their events:

        ```typescript
        --8<-- "examples/inline/typescript/agents/custom-agents/003-key-capabilities-within-the-core-asynchr.ts"
        ```

    2.  **Managing State:** Read from and write to the session state object (`ctx.session.state`) to pass data between sub-agent calls or make decisions:

        ```typescript
        --8<-- "examples/inline/typescript/agents/custom-agents/004-key-capabilities-within-the-core-asynchr.ts"
        ```

    3. **Implementing Control Flow:** Use standard TypeScript/JavaScript constructs (`if`/`else`, `for`/`while` loops, `try`/`catch`) to create sophisticated, conditional, or iterative workflows involving your sub-agents.

=== "Go"

    1. **Calling Sub-Agents:** You invoke sub-agents by calling their `Run` method.

          ```go
          --8<-- "examples/inline/go/agents/custom-agents/005-key-capabilities-within-the-core-asynchr.go.txt"
          ```

    2. **Managing State:** Read from and write to the session state to pass data between sub-agent calls or make decisions.
          ```go
          --8<-- "examples/inline/go/agents/custom-agents/006-key-capabilities-within-the-core-asynchr.go.txt"
          ```

    3. **Implementing Control Flow:** Use standard Go constructs (`if`/`else`, `for`/`switch` loops, goroutines, channels) to create sophisticated, conditional, or iterative workflows involving your sub-agents.

=== "Java"

    1. **Calling Sub-Agents:** You invoke sub-agents (which are typically stored as instance attributes or objects) using their asynchronous run method and return their event streams:

           You typically chain `Flowable`s from sub-agents using RxJava operators like `concatWith`, `flatMapPublisher`, or `concatArray`.

           ```java
           --8<-- "examples/inline/java/agents/custom-agents/007-key-capabilities-within-the-core-asynchr.java"
           ```
           The `Flowable.defer()` is often used for subsequent stages if their execution depends on the completion or state after prior stages.

    2. **Managing State:** Read from and write to the session state to pass data between sub-agent calls or make decisions. The session state is a `java.util.concurrent.ConcurrentMap<String, Object>` obtained via `ctx.session().state()`.

        ```java
        --8<-- "examples/inline/java/agents/custom-agents/008-key-capabilities-within-the-core-asynchr.java"
        ```

    3. **Implementing Control Flow:** Use standard language constructs (`if`/`else`, loops, `try`/`catch`) combined with reactive operators (RxJava) to create sophisticated workflows.

          *   **Conditional:** `Flowable.defer()` to choose which `Flowable` to subscribe to based on a condition, or `filter()` if you're filtering events within a stream.
          *   **Iterative:** Operators like `repeat()`, `retry()`, or by structuring your `Flowable` chain to recursively call parts of itself based on conditions (often managed with `flatMapPublisher` or `concatMap`).

## Managing sub-agents and state

Typically, a custom agent orchestrates other agents (like `LlmAgent`, `LoopAgent`, etc.).

* **Initialization:** You usually pass instances of these sub-agents into your custom agent's constructor and store them as instance fields/attributes (e.g., `this.story_generator = story_generator_instance` or `self.story_generator = story_generator_instance`). This makes them accessible within the custom agent's core asynchronous execution logic (such as: `_run_async_impl` method).
* **Sub Agents List:** When initializing the `BaseAgent` using it's `super()` constructor, you should pass a `sub agents` list. This list tells the ADK framework about the agents that are part of this custom agent's immediate hierarchy. It's important for framework features like lifecycle management, introspection, and potentially future routing capabilities, even if your core execution logic (`_run_async_impl`) calls the agents directly via `self.xxx_agent`. Include the agents that your custom logic directly invokes at the top level.
* **State:** As mentioned, `ctx.session.state` is the standard way sub-agents (especially `LlmAgent`s using `output key`) communicate results back to the orchestrator and how the orchestrator passes necessary inputs down.

## Agent-based workflow primitives

The following sections detail the core ADK primitives—such as agent hierarchy,
workflow agents, and interaction mechanisms—that enable you to construct and
manage these multi-agent systems effectively. ADK provides core building
blocks—primitives—that enable you to structure and manage interactions within
your multi-agent system.

!!! Note

    The specific parameters or method names for the primitives may vary slightly by
    SDK language, for example `sub_agents` in Python, and `subAgents` in Java. Refer
    to the language-specific API documentation for details.

### Agent hierarchy: Parent agents and sub-agents

The foundation for structuring multi-agent systems is the parent-child relationship defined in `BaseAgent`.

* **Establishing Hierarchy:** You create a tree structure by passing a list of agent instances to the `sub_agents` argument when initializing a parent agent. ADK automatically sets the `parent_agent` attribute on each child agent during initialization.
* **Single Parent Rule:** An agent instance can only be added as a sub-agent once. Attempting to assign a second parent will result in a `ValueError`.
* **Importance:** This hierarchy defines the scope for [Workflow Agents](#workflow-agents-as-orchestrators) and influences the potential targets for LLM-Driven Delegation. You can navigate the hierarchy using `agent.parent_agent` or find descendants using `agent.find_agent(name)`.

=== "Python"

    ```python
    --8<-- "examples/inline/python/agents/custom-agents/009-agent-hierarchy-parent-agents-and-sub-ag.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/agents/custom-agents/010-agent-hierarchy-parent-agents-and-sub-ag.ts"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/agents/custom-agents/011-agent-hierarchy-parent-agents-and-sub-ag.go.txt"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/agents/custom-agents/012-agent-hierarchy-parent-agents-and-sub-ag.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/agents/multi-agent/MultiAgentExample.kt:custom_agent"
    --8<-- "examples/kotlin/snippets/agents/multi-agent/MultiAgentExample.kt:hierarchy"
    ```

### Workflow agents as orchestrators

ADK includes specialized agents derived from `BaseAgent` that don't perform tasks themselves but orchestrate the execution flow of their `sub_agents`.

* **[`SequentialAgent`](workflow-agents/sequential-agents.md):** Executes its `sub_agents` one after another in the order they are listed.
    * **Context:** Passes the *same* [`InvocationContext`](../runtime/index.md) sequentially, allowing agents to easily pass results via shared state.

=== "Python"

    ```python
    --8<-- "examples/inline/python/agents/custom-agents/013-workflow-agents-as-orchestrators.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/agents/custom-agents/014-workflow-agents-as-orchestrators.ts"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/agents/custom-agents/015-workflow-agents-as-orchestrators.go.txt"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/agents/custom-agents/016-workflow-agents-as-orchestrators.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/agents/multi-agent/MultiAgentExample.kt:sequential_pipeline"
    ```

* **[`ParallelAgent`](workflow-agents/parallel-agents.md):** Executes its `sub_agents` in parallel. Events from sub-agents may be interleaved.
    * **Context:** Modifies the `InvocationContext.branch` for each child agent (e.g., `ParentBranch.ChildName`), providing a distinct contextual path which can be useful for isolating history in some memory implementations.
    * **State:** Despite different branches, all parallel children access the *same shared* `session.state`, enabling them to read initial state and write results (use distinct keys to avoid race conditions).

=== "Python"

    ```python
    --8<-- "examples/inline/python/agents/custom-agents/017-workflow-agents-as-orchestrators.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/agents/custom-agents/018-workflow-agents-as-orchestrators.ts"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/agents/custom-agents/019-workflow-agents-as-orchestrators.go.txt"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/agents/custom-agents/020-workflow-agents-as-orchestrators.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/agents/multi-agent/MultiAgentExample.kt:parallel_execution"
    ```

  * **[`LoopAgent`](workflow-agents/loop-agents.md):** Executes its `sub_agents` sequentially in a loop.
      * **Termination:** The loop stops if the optional `max_iterations` is reached, or if any sub-agent returns an [`Event`](../events/index.md) with `escalate=True` in its Event Actions.
      * **Context & State:** Passes the *same* `InvocationContext` in each iteration, allowing state changes (e.g., counters, flags) to persist across loops.

=== "Python"

      ```python
      --8<-- "examples/inline/python/agents/custom-agents/021-workflow-agents-as-orchestrators.py"
      ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/agents/custom-agents/022-workflow-agents-as-orchestrators.ts"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/agents/custom-agents/023-workflow-agents-as-orchestrators.go.txt"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/agents/custom-agents/024-workflow-agents-as-orchestrators.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/agents/multi-agent/MultiAgentExample.kt:check_condition_agent"
    --8<-- "examples/kotlin/snippets/agents/multi-agent/MultiAgentExample.kt:loop_with_condition"
    ```

### Interaction and communication mechanisms

Agents within a system often need to exchange data or trigger actions in one another. ADK facilitates this through:

#### Shared session state

The most fundamental way for agents operating within the same invocation (and thus sharing the same [`Session`](/sessions/session/) object via the `InvocationContext`) to communicate passively.

* **Mechanism:** One agent (or its tool/callback) writes a value (`context.state['data_key'] = processed_data`), and a subsequent agent reads it (`data = context.state.get('data_key')`). State changes are tracked via [`CallbackContext`](../callbacks/index.md).
* **Convenience:** The `output_key` property on [`LlmAgent`](llm-agents.md) automatically saves the agent's final response text (or structured output) to the specified state key.
* **Nature:** Asynchronous, passive communication. Ideal for pipelines orchestrated by `SequentialAgent` or passing data across `LoopAgent` iterations.
* **See Also:** [State Management](../sessions/state.md)

!!! note "Invocation Context and `temp:` State"
    When a parent agent invokes a sub-agent, it passes the same `InvocationContext`. This means they share the same temporary (`temp:`) state, which is ideal for passing data that is only relevant for the current turn.

=== "Python"

    ```python
    --8<-- "examples/inline/python/agents/custom-agents/025-shared-session-state.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/agents/custom-agents/026-shared-session-state.ts"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/agents/custom-agents/027-shared-session-state.go.txt"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/agents/custom-agents/028-shared-session-state.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/agents/multi-agent/MultiAgentExample.kt:output_key_state"
    ```

#### LLM delegation and agent transfer {#delegation}

Leverages an [`LlmAgent`](llm-agents.md)'s understanding to dynamically route tasks to other suitable agents within the hierarchy.

* **Mechanism:** The agent's LLM generates a specific function call: `transfer_to_agent(agent_name='target_agent_name')`.
* **Handling:** The `AutoFlow`, used by default when sub-agents are present or transfer isn't disallowed, intercepts this call. It identifies the target agent using `root_agent.find_agent()` and updates the `InvocationContext` to switch execution focus.
* **Requires:** The calling `LlmAgent` needs clear `instructions` on when to transfer, and potential target agents need distinct `description`s for the LLM to make informed decisions. Transfer scope (parent, sub-agent, siblings) can be configured on the `LlmAgent`.
* **Nature:** Dynamic, flexible routing based on LLM interpretation.

=== "Python"

    ```python
    --8<-- "examples/inline/python/agents/custom-agents/029-llm-delegation-and-agent-transfer-delega.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/agents/custom-agents/030-llm-delegation-and-agent-transfer-delega.ts"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/agents/custom-agents/031-llm-delegation-and-agent-transfer-delega.go.txt"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/agents/custom-agents/032-llm-delegation-and-agent-transfer-delega.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/agents/multi-agent/MultiAgentExample.kt:llm_transfer"
    ```

#### Explicit invocation with `AgentTool`

Allows an [`LlmAgent`](llm-agents.md) to treat another `BaseAgent` instance as a callable function or
[Tool](/tools-custom/).

* **Mechanism:** Wrap the target agent instance in `AgentTool` and include it in the parent `LlmAgent`'s `tools` list. `AgentTool` generates a corresponding function declaration for the LLM.
* **Handling:** When the parent LLM generates a function call targeting the `AgentTool`, the framework executes `AgentTool.run_async`. This method runs the target agent, captures its final response, forwards any state/artifact changes back to the parent's context, and returns the response as the tool's result.
* **Nature:** Synchronous (within the parent's flow), explicit, controlled invocation like any other tool.
* **(Note:** `AgentTool` needs to be imported and used explicitly).

=== "Python"

    ```python
    --8<-- "examples/inline/python/agents/custom-agents/033-explicit-invocation-with-agenttool.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/agents/custom-agents/034-explicit-invocation-with-agenttool.ts"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/agents/custom-agents/035-explicit-invocation-with-agenttool.go.txt"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/agents/custom-agents/036-explicit-invocation-with-agenttool.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/agents/multi-agent/MultiAgentExample.kt:agent_as_tool"
    ```

These primitives provide the flexibility to design multi-agent interactions ranging from tightly coupled sequential workflows to dynamic, LLM-driven delegation networks.

## Design pattern example: StoryFlow Agent

Let's illustrate the power of custom agents with an example pattern: a multi-stage content generation workflow with conditional logic.

**Goal:** Create a system that generates a story, iteratively refines it through critique and revision, performs final checks, and crucially, *regenerates the story if the final tone check fails*.

**Why Custom?** The core requirement driving the need for a custom agent here is the **conditional regeneration based on the tone check**. Standard workflow agents don't have built-in conditional branching based on the outcome of a sub-agent's task. We need custom logic (`if tone == "negative": ...`) within the orchestrator.

---

### Part 1: Simplified custom agent initialization

=== "Python"

    We define the `StoryFlowAgent` inheriting from `BaseAgent`. In `__init__`, we store the necessary sub-agents (passed in) as instance attributes and tell the `BaseAgent` framework about the top-level agents this custom agent will directly orchestrate.

    ```python
    --8<-- "examples/python/snippets/agents/custom-agent/storyflow_agent.py:init"
    ```

=== "TypeScript"

    We define the `StoryFlowAgent` by extending `BaseAgent`. In its constructor, we:
    1.  Create any internal composite agents (like `LoopAgent` or `SequentialAgent`).
    2.  Pass the list of all top-level sub-agents to the `super()` constructor.
    3.  Store the sub-agents (passed in or created internally) as instance properties (e.g., `this.storyGenerator`) so they can be accessed in the custom `runImpl` logic.

    ```typescript
    --8<-- "examples/typescript/snippets/agents/custom-agent/storyflow_agent.ts:init"
    ```

=== "Go"

    We define the `StoryFlowAgent` struct and a constructor. In the constructor, we store the necessary sub-agents and tell the `BaseAgent` framework about the top-level agents this custom agent will directly orchestrate.

    ```go
    --8<-- "examples/go/snippets/agents/custom-agent/storyflow_agent.go:init"
    ```

=== "Java"

    We define the `StoryFlowAgentExample` by extending `BaseAgent`. In its **constructor**, we store the necessary sub-agent instances (passed as parameters) as instance fields. These top-level sub-agents, which this custom agent will directly orchestrate, are also passed to the `super` constructor of `BaseAgent` as a list.

    ```java
    --8<-- "examples/java/snippets/src/main/java/agents/StoryFlowAgentExample.java:init"
    ```

---

### Part 2: Define custom execution logic

=== "Python"

    This method orchestrates the sub-agents using standard Python async/await and control flow.

    ```python
    --8<-- "examples/python/snippets/agents/custom-agent/storyflow_agent.py:executionlogic"
    ```
    **Explanation of Logic:**

    1. The initial `story_generator` runs. Its output is expected to be in `ctx.session.state["current_story"]`.
    2. The `loop_agent` runs, which internally calls the `critic` and `reviser` sequentially for `max_iterations` times. They read/write `current_story` and `criticism` from/to the state.
    3. The `sequential_agent` runs, calling `grammar_check` then `tone_check`, reading `current_story` and writing `grammar_suggestions` and `tone_check_result` to the state.
    4. **Custom Part:** The `if` statement checks the `tone_check_result` from the state. If it's "negative", the `story_generator` is called *again*, overwriting the `current_story` in the state. Otherwise, the flow ends.

=== "TypeScript"

    The `runImpl` method orchestrates the sub-agents using standard TypeScript `async`/`await` and control flow. The `runLiveImpl` is also added to handle live streaming scenarios.

    ```typescript
    --8<-- "examples/typescript/snippets/agents/custom-agent/storyflow_agent.ts:executionlogic"
    ```
    **Explanation of Logic:**

    1.  The initial `storyGenerator` runs. Its output is expected to be in `ctx.session.state['current_story']`.
    2.  The `loopAgent` runs, which internally calls the `critic` and `reviser` sequentially for `maxIterations` times. They read/write `current_story` and `criticism` from/to the state.
    3.  The `sequentialAgent` runs, calling `grammarCheck` then `toneCheck`, reading `current_story` and writing `grammar_suggestions` and `tone_check_result` to the state.
    4.  **Custom Part:** The `if` statement checks the `tone_check_result` from the state. If it's "negative", the `storyGenerator` is called *again*, overwriting the `current_story` in the state. Otherwise, the flow ends.

=== "Go"

    The `Run` method orchestrates the sub-agents by calling their respective `Run` methods in a loop and yielding their events.

    ```go
    --8<-- "examples/go/snippets/agents/custom-agent/storyflow_agent.go:executionlogic"
    ```
    **Explanation of Logic:**

    1. The initial `storyGenerator` runs. Its output is expected to be in the session state under the key `"current_story"`.
    2. The `revisionLoopAgent` runs, which internally calls the `critic` and `reviser` sequentially for `max_iterations` times. They read/write `current_story` and `criticism` from/to the state.
    3. The `postProcessorAgent` runs, calling `grammar_check` then `tone_check`, reading `current_story` and writing `grammar_suggestions` and `tone_check_result` to the state.
    4. **Custom Part:** The code checks the `tone_check_result` from the state. If it's "negative", the `story_generator` is called *again*, overwriting the `current_story` in the state. Otherwise, the flow ends.

=== "Java"

    The `runAsyncImpl` method orchestrates the sub-agents using RxJava's Flowable streams and operators for asynchronous control flow.

    ```java
    --8<-- "examples/java/snippets/src/main/java/agents/StoryFlowAgentExample.java:executionlogic"
    ```
    **Explanation of Logic:**

    1. The initial `storyGenerator.runAsync(invocationContext)` Flowable is executed. Its output is expected to be in `invocationContext.session().state().get("current_story")`.
    2. The `loopAgent's` Flowable runs next (due to `Flowable.concatArray` and `Flowable.defer`). The LoopAgent internally calls the `critic` and `reviser` sub-agents sequentially for up to `maxIterations`. They read/write `current_story` and `criticism` from/to the state.
    3. Then, the `sequentialAgent's` Flowable executes. It calls the `grammar_check` then `tone_check`, reading `current_story` and writing `grammar_suggestions` and `tone_check_result` to the state.
    4. **Custom Part:** After the sequentialAgent completes, logic within a `Flowable.defer` checks the "tone_check_result" from `invocationContext.session().state()`. If it's "negative", the `storyGenerator` Flowable is *conditionally concatenated* and executed again, overwriting "current_story". Otherwise, an empty Flowable is used, and the overall workflow proceeds to completion.

---

### Part 3: Define LLM sub-agents

These are standard `LlmAgent` definitions, responsible for specific tasks. Their `output key` parameter is crucial for placing results into the `session.state` where other agents or the custom orchestrator can access them.

!!! tip "Direct State Injection in Instructions"
    Notice the `story_generator`'s instruction. The `{var}` syntax is a placeholder. Before the instruction is sent to the LLM, the ADK framework automatically replaces (Example:`{topic}`) with the value of `session.state['topic']`. This is the recommended way to provide context to an agent, using templating in the instructions. For more details, see the [State documentation](../sessions/state.md#accessing-session-state-in-agent-instructions).

=== "Python"

    ```python
    --8<-- "examples/inline/python/agents/custom-agents/037-part-3-define-llm-sub-agents.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/agents/custom-agent/storyflow_agent.ts:llmagents"
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/agents/custom-agent/storyflow_agent.go:llmagents"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/agents/StoryFlowAgentExample.java:llmagents"
    ```

---

### Part 4: Instantiate and run the custom agent

Finally, you instantiate your `StoryFlowAgent` and use the `Runner` as usual.

=== "Python"

    ```python
    --8<-- "examples/python/snippets/agents/custom-agent/storyflow_agent.py:story_flow_agent"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/agents/custom-agent/storyflow_agent.ts:story_flow_agent"
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/agents/custom-agent/storyflow_agent.go:story_flow_agent"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/agents/StoryFlowAgentExample.java:story_flow_agent"
    ```

*(Note: The full runnable code, including imports and execution logic, can be found linked below.)*

---

### Storyflow Agent code listing

???+ "Storyflow Agent"

    === "Python"

        ```python
        --8<-- "examples/inline/python/agents/custom-agents/038-storyflow-agent-code-listing.py"
        ```

    === "TypeScript"

        ```typescript
        --8<-- "examples/inline/typescript/agents/custom-agents/039-storyflow-agent-code-listing.ts"
        ```

    === "Go"

        ```go
        --8<-- "examples/inline/go/agents/custom-agents/040-storyflow-agent-code-listing.go.txt"
        ```

    === "Java"

        ```java
        --8<-- "examples/inline/java/agents/custom-agents/041-storyflow-agent-code-listing.java"
        ```
