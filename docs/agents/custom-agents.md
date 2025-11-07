# Custom agents

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

Custom agents provide the ultimate flexibility in ADK, allowing you to define **arbitrary orchestration logic** by inheriting directly from `BaseAgent` and implementing your own control flow. This goes beyond the predefined patterns of `SequentialAgent`, `LoopAgent`, and `ParallelAgent`, enabling you to build highly specific and complex agentic workflows.

!!! warning "Advanced Concept"

    Building custom agents by directly implementing `_run_async_impl` (or its equivalent in other languages) provides powerful control but is more complex than using the predefined `LlmAgent` or standard `WorkflowAgent` types. We recommend understanding those foundational agent types first before tackling custom orchestration logic.

## Introduction: Beyond Predefined Workflows

### What is a Custom Agent?

A Custom Agent is essentially any class you create that inherits from `google.adk.agents.BaseAgent` and implements its core execution logic within the `_run_async_impl` asynchronous method. You have complete control over how this method calls other agents (sub-agents), manages state, and handles events. 

!!! Note
    The specific method name for implementing an agent's core asynchronous logic may vary slightly by SDK language (e.g., `runAsyncImpl` in Java, `_run_async_impl` in Python). Refer to the language-specific API documentation for details.

### Why Use Them?

While the standard [Workflow Agents](workflow-agents/index.md) (`SequentialAgent`, `LoopAgent`, `ParallelAgent`) cover common orchestration patterns, you'll need a Custom agent when your requirements include:

* **Conditional Logic:** Executing different sub-agents or taking different paths based on runtime conditions or the results of previous steps.
* **Complex State Management:** Implementing intricate logic for maintaining and updating state throughout the workflow beyond simple sequential passing.
* **External Integrations:** Incorporating calls to external APIs, databases, or custom libraries directly within the orchestration flow control.
* **Dynamic Agent Selection:** Choosing which sub-agent(s) to run next based on dynamic evaluation of the situation or input.
* **Unique Workflow Patterns:** Implementing orchestration logic that doesn't fit the standard sequential, parallel, or loop structures.


![intro_components.png](../assets/custom-agent-flow.png)


## Implementing Custom Logic:

The core of any custom agent is the method where you define its unique asynchronous behavior. This method allows you to orchestrate sub-agents and manage the flow of execution.

=== "Python"

      The heart of any custom agent is the `_run_async_impl` method. This is where you define its unique behavior.
      
      * **Signature:** `async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:`
      * **Asynchronous Generator:** It must be an `async def` function and return an `AsyncGenerator`. This allows it to `yield` events produced by sub-agents or its own logic back to the runner.
      * **`ctx` (InvocationContext):** Provides access to crucial runtime information, most importantly `ctx.session.state`, which is the primary way to share data between steps orchestrated by your custom agent.

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

**Key Capabilities within the Core Asynchronous Method:**

=== "Python"

    1. **Calling Sub-Agents:** You invoke sub-agents (which are typically stored as instance attributes like `self.my_llm_agent`) using their `run_async` method and yield their events:

          ```python
          async for event in self.some_sub_agent.run_async(ctx):
              # Optionally inspect or log the event
              yield event # Pass the event up
          ```

    2. **Managing State:** Read from and write to the session state dictionary (`ctx.session.state`) to pass data between sub-agent calls or make decisions:
          ```python
          # Read data set by a previous agent
          previous_result = ctx.session.state.get("some_key")
      
          # Make a decision based on state
          if previous_result == "some_value":
              # ... call a specific sub-agent ...
          else:
              # ... call another sub-agent ...
      
          # Store a result for a later step (often done via a sub-agent's output_key)
          # ctx.session.state["my_custom_result"] = "calculated_value"
          ```

    3. **Implementing Control Flow:** Use standard Python constructs (`if`/`elif`/`else`, `for`/`while` loops, `try`/`except`) to create sophisticated, conditional, or iterative workflows involving your sub-agents.

=== "Go"

    1. **Calling Sub-Agents:** You invoke sub-agents by calling their `Run` method.

          ```go
          // Example: Running one sub-agent and yielding its events
          for event, err := range someSubAgent.Run(ctx) {
              if err != nil {
                  // Handle or propagate the error
                  return
              }
              // Yield the event up to the caller
              if !yield(event, nil) {
                return
              }
          }
          ```

    2. **Managing State:** Read from and write to the session state to pass data between sub-agent calls or make decisions.
          ```go
          // The `ctx` (`agent.InvocationContext`) is passed directly to your agent's `Run` function.
          // Read data set by a previous agent
          previousResult, err := ctx.Session().State().Get("some_key")
          if err != nil {
              // Handle cases where the key might not exist yet
          }

          // Make a decision based on state
          if val, ok := previousResult.(string); ok && val == "some_value" {
              // ... call a specific sub-agent ...
          } else {
              // ... call another sub-agent ...
          }

          // Store a result for a later step
          if err := ctx.Session().State().Set("my_custom_result", "calculated_value"); err != nil {
              // Handle error
          }
          ```

    3. **Implementing Control Flow:** Use standard Go constructs (`if`/`else`, `for`/`switch` loops, goroutines, channels) to create sophisticated, conditional, or iterative workflows involving your sub-agents.

=== "Java"

    1. **Calling Sub-Agents:** You invoke sub-agents (which are typically stored as instance attributes or objects) using their asynchronous run method and return their event streams:

           You typically chain `Flowable`s from sub-agents using RxJava operators like `concatWith`, `flatMapPublisher`, or `concatArray`.

           ```java
           // Example: Running one sub-agent
           // return someSubAgent.runAsync(ctx);
      
           // Example: Running sub-agents sequentially
           Flowable<Event> firstAgentEvents = someSubAgent1.runAsync(ctx)
               .doOnNext(event -> System.out.println("Event from agent 1: " + event.id()));
      
           Flowable<Event> secondAgentEvents = Flowable.defer(() ->
               someSubAgent2.runAsync(ctx)
                   .doOnNext(event -> System.out.println("Event from agent 2: " + event.id()))
           );
      
           return firstAgentEvents.concatWith(secondAgentEvents);
           ```
           The `Flowable.defer()` is often used for subsequent stages if their execution depends on the completion or state after prior stages.

    2. **Managing State:** Read from and write to the session state to pass data between sub-agent calls or make decisions. The session state is a `java.util.concurrent.ConcurrentMap<String, Object>` obtained via `ctx.session().state()`.
        
        ```java
        // Read data set by a previous agent
        Object previousResult = ctx.session().state().get("some_key");

        // Make a decision based on state
        if ("some_value".equals(previousResult)) {
            // ... logic to include a specific sub-agent's Flowable ...
        } else {
            // ... logic to include another sub-agent's Flowable ...
        }

        // Store a result for a later step (often done via a sub-agent's output_key)
        // ctx.session().state().put("my_custom_result", "calculated_value");
        ```

    3. **Implementing Control Flow:** Use standard language constructs (`if`/`else`, loops, `try`/`catch`) combined with reactive operators (RxJava) to create sophisticated workflows.

          *   **Conditional:** `Flowable.defer()` to choose which `Flowable` to subscribe to based on a condition, or `filter()` if you're filtering events within a stream.
          *   **Iterative:** Operators like `repeat()`, `retry()`, or by structuring your `Flowable` chain to recursively call parts of itself based on conditions (often managed with `flatMapPublisher` or `concatMap`).

## Managing Sub-Agents and State

Typically, a custom agent orchestrates other agents (like `LlmAgent`, `LoopAgent`, etc.).

* **Initialization:** You usually pass instances of these sub-agents into your custom agent's constructor and store them as instance fields/attributes (e.g., `this.story_generator = story_generator_instance` or `self.story_generator = story_generator_instance`). This makes them accessible within the custom agent's core asynchronous execution logic (such as: `_run_async_impl` method).
* **Sub Agents List:** When initializing the `BaseAgent` using it's `super()` constructor, you should pass a `sub agents` list. This list tells the ADK framework about the agents that are part of this custom agent's immediate hierarchy. It's important for framework features like lifecycle management, introspection, and potentially future routing capabilities, even if your core execution logic (`_run_async_impl`) calls the agents directly via `self.xxx_agent`. Include the agents that your custom logic directly invokes at the top level.
* **State:** As mentioned, `ctx.session.state` is the standard way sub-agents (especially `LlmAgent`s using `output key`) communicate results back to the orchestrator and how the orchestrator passes necessary inputs down.

## Design Pattern Example: `StoryFlowAgent`

Let's illustrate the power of custom agents with an example pattern: a multi-stage content generation workflow with conditional logic.

**Goal:** Create a system that generates a story, iteratively refines it through critique and revision, performs final checks, and crucially, *regenerates the story if the final tone check fails*.

**Why Custom?** The core requirement driving the need for a custom agent here is the **conditional regeneration based on the tone check**. Standard workflow agents don't have built-in conditional branching based on the outcome of a sub-agent's task. We need custom logic (`if tone == "negative": ...`) within the orchestrator.

---

### Part 1: Simplified custom agent Initialization { #part-1-simplified-custom-agent-initialization }

=== "Python"

    We define the `StoryFlowAgent` inheriting from `BaseAgent`. In `__init__`, we store the necessary sub-agents (passed in) as instance attributes and tell the `BaseAgent` framework about the top-level agents this custom agent will directly orchestrate.
    
    ```python
    --8<-- "examples/python/snippets/agents/custom-agent/storyflow_agent.py:init"
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

### Part 2: Defining the Custom Execution Logic { #part-2-defining-the-custom-execution-logic }

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

### Part 3: Defining the LLM Sub-Agents { #part-3-defining-the-llm-sub-agents }

These are standard `LlmAgent` definitions, responsible for specific tasks. Their `output key` parameter is crucial for placing results into the `session.state` where other agents or the custom orchestrator can access them.

!!! tip "Direct State Injection in Instructions"
    Notice the `story_generator`'s instruction. The `{var}` syntax is a placeholder. Before the instruction is sent to the LLM, the ADK framework automatically replaces (Example:`{topic}`) with the value of `session.state['topic']`. This is the recommended way to provide context to an agent, using templating in the instructions. For more details, see the [State documentation](../sessions/state.md#accessing-session-state-in-agent-instructions).

=== "Python"

    ```python
    GEMINI_2_FLASH = "gemini-2.0-flash" # Define model constant
    --8<-- "examples/python/snippets/agents/custom-agent/storyflow_agent.py:llmagents"
    ```
=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/agents/StoryFlowAgentExample.java:llmagents"
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/agents/custom-agent/storyflow_agent.go:llmagents"
    ```

---

### Part 4: Instantiating and Running the custom agent { #part-4-instantiating-and-running-the-custom-agent }

Finally, you instantiate your `StoryFlowAgent` and use the `Runner` as usual.

=== "Python"

    ```python
    --8<-- "examples/python/snippets/agents/custom-agent/storyflow_agent.py:story_flow_agent"
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

## Full Code Example

???+ "Storyflow Agent"

    === "Python"
    
        ```python
        # Full runnable code for the StoryFlowAgent example
        --8<-- "examples/python/snippets/agents/custom-agent/storyflow_agent.py"
        ```
    
    === "Go"

        ```go
        # Full runnable code for the StoryFlowAgent example
        --8<-- "examples/go/snippets/agents/custom-agent/storyflow_agent.go:full_code"
        ```

    === "Java"
    
        ```java
        # Full runnable code for the StoryFlowAgent example
        --8<-- "examples/java/snippets/src/main/java/agents/StoryFlowAgentExample.java:full_code"
        ```
