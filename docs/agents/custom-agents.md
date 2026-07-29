# Custom agent template workflows

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">Typescript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
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

=== "TypeScript"

    1.  **Calling Sub-Agents:** You invoke sub-agents (which are typically stored as instance properties like `this.myLlmAgent`) using their `run` method and yield their events:

        ```typescript
        for await (const event of this.someSubAgent.runAsync(ctx)) {
            // Optionally inspect or log the event
            yield event; // Pass the event up to the runner
        }
        ```

    2.  **Managing State:** Read from and write to the session state object (`ctx.session.state`) to pass data between sub-agent calls or make decisions:

        ```typescript
        // Read data set by a previous agent
        const previousResult = ctx.session.state['some_key'];

        // Make a decision based on state
        if (previousResult === 'some_value') {
          // ... call a specific sub-agent ...
        } else {
          // ... call another sub-agent ...
        }

        // Store a result for a later step (often done via a sub-agent's outputKey)
        // ctx.session.state['my_custom_result'] = 'calculated_value';
        ```

    3. **Implementing Control Flow:** Use standard TypeScript/JavaScript constructs (`if`/`else`, `for`/`while` loops, `try`/`catch`) to create sophisticated, conditional, or iterative workflows involving your sub-agents.

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
    # Conceptual Example: Defining Hierarchy
    from google.adk.agents import LlmAgent, BaseAgent


    # Define individual agents
    greeter = LlmAgent(name="Greeter", model="gemini-flash-latest")
    task_doer = BaseAgent(name="TaskExecutor") # Custom non-LLM agent


    # Create parent agent and assign children via sub_agents
    coordinator = LlmAgent(
        name="Coordinator",
        model="gemini-flash-latest",
        description="I coordinate greetings and tasks.",
        sub_agents=[ # Assign sub_agents here
            greeter,
            task_doer
        ]
    )


    # Framework automatically sets:
    # assert greeter.parent_agent == coordinator
    # assert task_doer.parent_agent == coordinator
    ```

=== "Typescript"

    ```typescript
    // Conceptual Example: Defining Hierarchy
    import { LlmAgent, BaseAgent, InvocationContext } from '@google/adk';
    import type { Event, createEventActions } from '@google/adk';

    class TaskExecutorAgent extends BaseAgent {
      async *runAsyncImpl(context: InvocationContext): AsyncGenerator<Event, void, void> {
        yield {
          id: 'event-1',
          invocationId: context.invocationId,
          author: this.name,
          content: { parts: [{ text: 'Task completed!' }] },
          actions: createEventActions(),
          timestamp: Date.now(),
        };
      }
      async *runLiveImpl(context: InvocationContext): AsyncGenerator<Event, void, void> {
        this.runAsyncImpl(context);
      }
    }

    // Define individual agents
    const greeter = new LlmAgent({name: 'Greeter', model: 'gemini-flash-latest'});
    const taskDoer = new TaskExecutorAgent({name: 'TaskExecutor'}); // Custom non-LLM agent

    // Create parent agent and assign children via subAgents
    const coordinator = new LlmAgent({
        name: 'Coordinator',
        model: 'gemini-flash-latest',
        description: 'I coordinate greetings and tasks.',
        subAgents: [ // Assign subAgents here
            greeter,
            taskDoer
        ],
    });

    // Framework automatically sets:
    // console.assert(greeter.parentAgent === coordinator);
    // console.assert(taskDoer.parentAgent === coordinator);
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/v2/agent"
        "google.golang.org/adk/v2/agent/llmagent"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:hierarchy"
    ```

=== "Java"

    ```java
    // Conceptual Example: Defining Hierarchy
    import com.google.adk.agents.SequentialAgent;
    import com.google.adk.agents.LlmAgent;


    // Define individual agents
    LlmAgent greeter = LlmAgent.builder().name("Greeter").model("gemini-flash-latest").build();
    SequentialAgent taskDoer = SequentialAgent.builder().name("TaskExecutor").subAgents(...).build(); // Sequential Agent


    // Create parent agent and assign sub_agents
    LlmAgent coordinator = LlmAgent.builder()
        .name("Coordinator")
        .model("gemini-flash-latest")
        .description("I coordinate greetings and tasks")
        .subAgents(greeter, taskDoer) // Assign sub_agents here
        .build();


    // Framework automatically sets:
    // assert greeter.parentAgent().equals(coordinator);
    // assert taskDoer.parentAgent().equals(coordinator);
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
    # Conceptual Example: Sequential Pipeline
    from google.adk.agents import SequentialAgent, LlmAgent

    step1 = LlmAgent(name="Step1_Fetch", output_key="data") # Saves output to state['data']
    step2 = LlmAgent(name="Step2_Process", instruction="Process data from {data}.")

    pipeline = SequentialAgent(name="MyPipeline", sub_agents=[step1, step2])
    # When pipeline runs, Step2 can access the state['data'] set by Step1.
    ```

=== "Typescript"

    ```typescript
    // Conceptual Example: Sequential Pipeline
    import { SequentialAgent, LlmAgent } from '@google/adk';

    const step1 = new LlmAgent({name: 'Step1_Fetch', outputKey: 'data'}); // Saves output to state['data']
    const step2 = new LlmAgent({name: 'Step2_Process', instruction: 'Process data from {data}.'});

    const pipeline = new SequentialAgent({name: 'MyPipeline', subAgents: [step1, step2]});
    // When pipeline runs, Step2 can access the state['data'] set by Step1.
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/v2/agent"
        "google.golang.org/adk/v2/agent/llmagent"
        "google.golang.org/adk/v2/agent/workflowagents/sequentialagent"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:sequential-pipeline"
    ```

=== "Java"

    ```java
    // Conceptual Example: Sequential Pipeline
    import com.google.adk.agents.SequentialAgent;
    import com.google.adk.agents.LlmAgent;

    LlmAgent step1 = LlmAgent.builder().name("Step1_Fetch").outputKey("data").build(); // Saves output to state.get("data")
    LlmAgent step2 = LlmAgent.builder().name("Step2_Process").instruction("Process data from {data}.").build();

    SequentialAgent pipeline = SequentialAgent.builder().name("MyPipeline").subAgents(step1, step2).build();
    // When pipeline runs, Step2 can access the state.get("data") set by Step1.
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
    # Conceptual Example: Parallel Execution
    from google.adk.agents import ParallelAgent, LlmAgent

    fetch_weather = LlmAgent(name="WeatherFetcher", output_key="weather")
    fetch_news = LlmAgent(name="NewsFetcher", output_key="news")

    gatherer = ParallelAgent(name="InfoGatherer", sub_agents=[fetch_weather, fetch_news])
    # When gatherer runs, WeatherFetcher and NewsFetcher run concurrently.
    # A subsequent agent could read state['weather'] and state['news'].
    ```

=== "Typescript"

    ```typescript
    // Conceptual Example: Parallel Execution
    import { ParallelAgent, LlmAgent } from '@google/adk';

    const fetchWeather = new LlmAgent({name: 'WeatherFetcher', outputKey: 'weather'});
    const fetchNews = new LlmAgent({name: 'NewsFetcher', outputKey: 'news'});

    const gatherer = new ParallelAgent({name: 'InfoGatherer', subAgents: [fetchWeather, fetchNews]});
    // When gatherer runs, WeatherFetcher and NewsFetcher run concurrently.
    // A subsequent agent could read state['weather'] and state['news'].
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/v2/agent"
        "google.golang.org/adk/v2/agent/llmagent"
        "google.golang.org/adk/v2/agent/workflowagents/parallelagent"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:parallel-execution"
    ```

=== "Java"

    ```java
    // Conceptual Example: Parallel Execution
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.ParallelAgent;


    LlmAgent fetchWeather = LlmAgent.builder()
        .name("WeatherFetcher")
        .outputKey("weather")
        .build();


    LlmAgent fetchNews = LlmAgent.builder()
        .name("NewsFetcher")
        .instruction("news")
        .build();


    ParallelAgent gatherer = ParallelAgent.builder()
        .name("InfoGatherer")
        .subAgents(fetchWeather, fetchNews)
        .build();


    // When gatherer runs, WeatherFetcher and NewsFetcher run concurrently.
    // A subsequent agent could read state['weather'] and state['news'].
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
      # Conceptual Example: Loop with Condition
      from google.adk.agents import LoopAgent, LlmAgent, BaseAgent
      from google.adk.events import Event, EventActions
      from google.adk.agents.invocation_context import InvocationContext
      from typing import AsyncGenerator

      class CheckCondition(BaseAgent): # Custom agent to check state
          async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
              status = ctx.session.state.get("status", "pending")
              is_done = (status == "completed")
              yield Event(author=self.name, actions=EventActions(escalate=is_done)) # Escalate if done

      process_step = LlmAgent(name="ProcessingStep") # Agent that might update state['status']

      poller = LoopAgent(
          name="StatusPoller",
          max_iterations=10,
          sub_agents=[process_step, CheckCondition(name="Checker")]
      )
      # When poller runs, it executes process_step then Checker repeatedly
      # until Checker escalates (state['status'] == 'completed') or 10 iterations pass.
      ```

=== "Typescript"

    ```typescript
    // Conceptual Example: Loop with Condition
    import { LoopAgent, LlmAgent, BaseAgent, InvocationContext } from '@google/adk';
    import type { Event, createEventActions, EventActions } from '@google/adk';

    class CheckConditionAgent extends BaseAgent { // Custom agent to check state
        async *runAsyncImpl(ctx: InvocationContext): AsyncGenerator<Event> {
            const status = ctx.session.state['status'] || 'pending';
            const isDone = status === 'completed';
            yield createEvent({ author: 'check_condition', actions: createEventActions({ escalate: isDone }) });
        }

        async *runLiveImpl(ctx: InvocationContext): AsyncGenerator<Event> {
            // This is not implemented.
        }
    };

    const processStep = new LlmAgent({name: 'ProcessingStep'}); // Agent that might update state['status']

    const poller = new LoopAgent({
        name: 'StatusPoller',
        maxIterations: 10,
        // Executes its sub_agents sequentially in a loop
        subAgents: [processStep, new CheckConditionAgent ({name: 'Checker'})]
    });
    // When poller runs, it executes processStep then Checker repeatedly
    // until Checker escalates (state['status'] === 'completed') or 10 iterations pass.
    ```

=== "Go"

    ```go
    import (
        "iter"
        "google.golang.org/adk/v2/agent"
        "google.golang.org/adk/v2/agent/llmagent"
        "google.golang.org/adk/v2/agent/workflowagents/loopagent"
        "google.golang.org/adk/v2/session"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:loop-with-condition"
    ```

=== "Java"

    ```java
    // Conceptual Example: Loop with Condition
    // Custom agent to check state and potentially escalate
    public static class CheckConditionAgent extends BaseAgent {
      public CheckConditionAgent(String name, String description) {
        super(name, description, List.of(), null, null);
      }

      @Override
      protected Flowable<Event> runAsyncImpl(InvocationContext ctx) {
        String status = (String) ctx.session().state().getOrDefault("status", "pending");
        boolean isDone = "completed".equalsIgnoreCase(status);

        // Emit an event that signals to escalate (exit the loop) if the condition is met.
        // If not done, the escalate flag will be false or absent, and the loop continues.
        Event checkEvent = Event.builder()
                .author(name())
                .id(Event.generateEventId()) // Important to give events unique IDs
                .actions(EventActions.builder().escalate(isDone).build()) // Escalate if done
                .build();
        return Flowable.just(checkEvent);
      }
    }

    // Agent that might update state.put("status")
    LlmAgent processingStepAgent = LlmAgent.builder().name("ProcessingStep").build();
    // Custom agent instance for checking the condition
    CheckConditionAgent conditionCheckerAgent = new CheckConditionAgent(
        "ConditionChecker",
        "Checks if the status is 'completed'."
    );
    LoopAgent poller = LoopAgent.builder().name("StatusPoller").maxIterations(10).subAgents(processingStepAgent, conditionCheckerAgent).build();
    // When poller runs, it executes processingStepAgent then conditionCheckerAgent repeatedly
    // until Checker escalates (state.get("status") == "completed") or 10 iterations pass.
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
    # Conceptual Example: Using output_key and reading state
    from google.adk.agents import LlmAgent, SequentialAgent


    agent_A = LlmAgent(name="AgentA", instruction="Find the capital of France.", output_key="capital_city")
    agent_B = LlmAgent(name="AgentB", instruction="Tell me about the city stored in {capital_city}.")


    pipeline = SequentialAgent(name="CityInfo", sub_agents=[agent_A, agent_B])
    # AgentA runs, saves "Paris" to state['capital_city'].
    # AgentB runs, its instruction processor reads state['capital_city'] to get "Paris".
    ```

=== "Typescript"

    ```typescript
    // Conceptual Example: Using outputKey and reading state
    import { LlmAgent, SequentialAgent } from '@google/adk';

    const agentA = new LlmAgent({name: 'AgentA', instruction: 'Find the capital of France.', outputKey: 'capital_city'});
    const agentB = new LlmAgent({name: 'AgentB', instruction: 'Tell me about the city stored in {capital_city}.'});

    const pipeline = new SequentialAgent({name: 'CityInfo', subAgents: [agentA, agentB]});
    // AgentA runs, saves "Paris" to state['capital_city'].
    // AgentB runs, its instruction processor reads state['capital_city'] to get "Paris".
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/v2/agent"
        "google.golang.org/adk/v2/agent/llmagent"
        "google.golang.org/adk/v2/agent/workflowagents/sequentialagent"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:output-key-state"
    ```

=== "Java"

    ```java
    // Conceptual Example: Using outputKey and reading state
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.SequentialAgent;


    LlmAgent agentA = LlmAgent.builder()
        .name("AgentA")
        .instruction("Find the capital of France.")
        .outputKey("capital_city")
        .build();


    LlmAgent agentB = LlmAgent.builder()
        .name("AgentB")
        .instruction("Tell me about the city stored in {capital_city}.")
        .outputKey("capital_city")
        .build();


    SequentialAgent pipeline = SequentialAgent.builder().name("CityInfo").subAgents(agentA, agentB).build();
    // AgentA runs, saves "Paris" to state('capital_city').
    // AgentB runs, its instruction processor reads state.get("capital_city") to get "Paris".
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
    # Conceptual Setup: LLM Transfer
    from google.adk.agents import LlmAgent


    booking_agent = LlmAgent(name="Booker", description="Handles flight and hotel bookings.")
    info_agent = LlmAgent(name="Info", description="Provides general information and answers questions.")


    coordinator = LlmAgent(
        name="Coordinator",
        model="gemini-flash-latest",
        instruction="You are an assistant. Delegate booking tasks to Booker and info requests to Info.",
        description="Main coordinator.",
        # AutoFlow is typically used implicitly here
        sub_agents=[booking_agent, info_agent]
    )
    # If coordinator receives "Book a flight", its LLM should generate:
    # FunctionCall(name='transfer_to_agent', args={'agent_name': 'Booker'})
    # ADK framework then routes execution to booking_agent.
    ```

=== "Typescript"

    ```typescript
    // Conceptual Setup: LLM Transfer
    import { LlmAgent } from '@google/adk';

    const bookingAgent = new LlmAgent({name: 'Booker', description: 'Handles flight and hotel bookings.'});
    const infoAgent = new LlmAgent({name: 'Info', description: 'Provides general information and answers questions.'});

    const coordinator = new LlmAgent({
        name: 'Coordinator',
        model: 'gemini-flash-latest',
        instruction: 'You are an assistant. Delegate booking tasks to Booker and info requests to Info.',
        description: 'Main coordinator.',
        // AutoFlow is typically used implicitly here
        subAgents: [bookingAgent, infoAgent]
    });
    // If coordinator receives "Book a flight", its LLM should generate:
    // {functionCall: {name: 'transfer_to_agent', args: {agent_name: 'Booker'}}}
    // ADK framework then routes execution to bookingAgent.
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/v2/agent/llmagent"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:llm-transfer"
    ```

=== "Java"

    ```java
    // Conceptual Setup: LLM Transfer
    import com.google.adk.agents.LlmAgent;


    LlmAgent bookingAgent = LlmAgent.builder()
        .name("Booker")
        .description("Handles flight and hotel bookings.")
        .build();


    LlmAgent infoAgent = LlmAgent.builder()
        .name("Info")
        .description("Provides general information and answers questions.")
        .build();


    // Define the coordinator agent
    LlmAgent coordinator = LlmAgent.builder()
        .name("Coordinator")
        .model("gemini-flash-latest") // Or your desired model
        .instruction("You are an assistant. Delegate booking tasks to Booker and info requests to Info.")
        .description("Main coordinator.")
        // AutoFlow will be used by default (implicitly) because subAgents are present
        // and transfer is not disallowed.
        .subAgents(bookingAgent, infoAgent)
        .build();

    // If coordinator receives "Book a flight", its LLM should generate:
    // FunctionCall.builder.name("transferToAgent").args(ImmutableMap.of("agent_name", "Booker")).build()
    // ADK framework then routes execution to bookingAgent.
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
    # Conceptual Setup: Agent as a Tool
    from google.adk.agents import LlmAgent, BaseAgent
    from google.adk.tools import agent_tool
    from pydantic import BaseModel


    # Define a target agent (could be LlmAgent or custom BaseAgent)
    class ImageGeneratorAgent(BaseAgent): # Example custom agent
        name: str = "ImageGen"
        description: str = "Generates an image based on a prompt."
        # ... internal logic ...
        async def _run_async_impl(self, ctx): # Simplified run logic
            prompt = ctx.session.state.get("image_prompt", "default prompt")
            # ... generate image bytes ...
            image_bytes = b"..."
            yield Event(author=self.name, content=types.Content(parts=[types.Part.from_bytes(image_bytes, "image/png")]))


    image_agent = ImageGeneratorAgent()
    image_tool = agent_tool.AgentTool(agent=image_agent) # Wrap the agent


    # Parent agent uses the AgentTool
    artist_agent = LlmAgent(
        name="Artist",
        model="gemini-flash-latest",
        instruction="Create a prompt and use the ImageGen tool to generate the image.",
        tools=[image_tool] # Include the AgentTool
    )
    # Artist LLM generates a prompt, then calls:
    # FunctionCall(name='ImageGen', args={'image_prompt': 'a cat wearing a hat'})
    # Framework calls image_tool.run_async(...), which runs ImageGeneratorAgent.
    # The resulting image Part is returned to the Artist agent as the tool result.
    ```

=== "Typescript"

    ```typescript
    // Conceptual Setup: Agent as a Tool
    import { LlmAgent, BaseAgent, AgentTool, InvocationContext } from '@google/adk';
    import type { Part, createEvent, Event } from '@google/genai';

    // Define a target agent (could be LlmAgent or custom BaseAgent)
    class ImageGeneratorAgent extends BaseAgent { // Example custom agent
        constructor() {
            super({name: 'ImageGen', description: 'Generates an image based on a prompt.'});
        }
        // ... internal logic ...
        async *runAsyncImpl(ctx: InvocationContext): AsyncGenerator<Event> { // Simplified run logic
            const prompt = ctx.session.state['image_prompt'] || 'default prompt';
            // ... generate image bytes ...
            const imageBytes = new Uint8Array(); // placeholder
            const imagePart: Part = {inlineData: {data: Buffer.from(imageBytes).toString('base64'), mimeType: 'image/png'}};
            yield createEvent({content: {parts: [imagePart]}});
        }

        async *runLiveImpl(ctx: InvocationContext): AsyncGenerator<Event, void, void> {
            // Not implemented for this agent.
        }
    }

    const imageAgent = new ImageGeneratorAgent();
    const imageTool = new AgentTool({agent: imageAgent}); // Wrap the agent

    // Parent agent uses the AgentTool
    const artistAgent = new LlmAgent({
        name: 'Artist',
        model: 'gemini-flash-latest',
        instruction: 'Create a prompt and use the ImageGen tool to generate the image.',
        tools: [imageTool] // Include the AgentTool
    });
    // Artist LLM generates a prompt, then calls:
    // {functionCall: {name: 'ImageGen', args: {image_prompt: 'a cat wearing a hat'}}}
    // Framework calls imageTool.runAsync(...), which runs ImageGeneratorAgent.
    // The resulting image Part is returned to the Artist agent as the tool result.
    ```

=== "Go"

    ```go
    import (
        "fmt"
        "iter"
        "google.golang.org/adk/v2/agent"
        "google.golang.org/adk/v2/agent/llmagent"
        "google.golang.org/adk/v2/model"
        "google.golang.org/adk/v2/session"
        "google.golang.org/adk/v2/tool"
        "google.golang.org/adk/v2/tool/agenttool"
        "google.golang.org/genai"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:agent-as-tool"
    ```

=== "Java"

    ```java
    // Conceptual Setup: Agent as a Tool
    import com.google.adk.agents.BaseAgent;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.tools.AgentTool;

    // Example custom agent (could be LlmAgent or custom BaseAgent)
    public class ImageGeneratorAgent extends BaseAgent  {


      public ImageGeneratorAgent(String name, String description) {
        super(name, description, List.of(), null, null);
      }


      // ... internal logic ...
      @Override
      protected Flowable<Event> runAsyncImpl(InvocationContext invocationContext) { // Simplified run logic
        invocationContext.session().state().get("image_prompt");
        // Generate image bytes
        // ...


        Event responseEvent = Event.builder()
            .author(this.name())
            .content(Content.fromParts(Part.fromText("...")))
            .build();


        return Flowable.just(responseEvent);
      }


      @Override
      protected Flowable<Event> runLiveImpl(InvocationContext invocationContext) {
        return null;
      }
    }

    // Wrap the agent using AgentTool
    ImageGeneratorAgent imageAgent = new ImageGeneratorAgent("image_agent", "generates images");
    AgentTool imageTool = AgentTool.create(imageAgent);


    // Parent agent uses the AgentTool
    LlmAgent artistAgent = LlmAgent.builder()
            .name("Artist")
            .model("gemini-flash-latest")
            .instruction(
                    "You are an artist. Create a detailed prompt for an image and then " +
                            "use the 'ImageGen' tool to generate the image. " +
                            "The 'ImageGen' tool expects a single string argument named 'request' " +
                            "containing the image prompt. The tool will return a JSON string in its " +
                            "'result' field, containing 'image_base64', 'mime_type', and 'status'."
            )
            .description("An agent that can create images using a generation tool.")
            .tools(imageTool) // Include the AgentTool
            .build();


    // Artist LLM generates a prompt, then calls:
    // FunctionCall(name='ImageGen', args={'imagePrompt': 'a cat wearing a hat'})
    // Framework calls imageTool.runAsync(...), which runs ImageGeneratorAgent.
    // The resulting image Part is returned to the Artist agent as the tool result.
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
    GEMINI_2_FLASH = "gemini-flash-latest" # Define model constant
    --8<-- "examples/python/snippets/agents/custom-agent/storyflow_agent.py:llmagents"
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
        # Full runnable code for the StoryFlowAgent example
        --8<-- "examples/python/snippets/agents/custom-agent/storyflow_agent.py"
        ```

    === "TypeScript"

        ```typescript
        // Full runnable code for the StoryFlowAgent example

        --8<-- "examples/typescript/snippets/agents/custom-agent/storyflow_agent.ts"
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
