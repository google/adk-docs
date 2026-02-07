# Multi-Agent Systems in ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">Typescript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

As agentic applications grow in complexity, structuring them as a single, monolithic agent can become challenging to develop, maintain, and reason about. The Agent Development Kit (ADK) supports building sophisticated applications by composing multiple, distinct `BaseAgent` instances into a **Multi-Agent System (MAS)**.

In ADK, a multi-agent system is an application where different agents, often forming a hierarchy, collaborate or coordinate to achieve a larger goal. Structuring your application this way offers significant advantages, including enhanced modularity, specialization, reusability, maintainability, and the ability to define structured control flows using dedicated workflow agents.

You can compose various types of agents derived from `BaseAgent` to build these systems:

* **LLM Agents:** Agents powered by large language models. (See [LLM Agents](llm-agents.md))
* **Workflow Agents:** Specialized agents (`SequentialAgent`, `ParallelAgent`, `LoopAgent`) designed to manage the execution flow of their sub-agents. (See [Workflow Agents](workflow-agents/index.md))
* **Custom agents:** Your own agents inheriting from `BaseAgent` with specialized, non-LLM logic. (See [Custom Agents](custom-agents.md))

The following sections detail the core ADK primitives—such as agent hierarchy, workflow agents, and interaction mechanisms—that enable you to construct and manage these multi-agent systems effectively.

## 1. ADK Primitives for Agent Composition { #adk-primitives-for-agent-composition }

ADK provides core building blocks—primitives—that enable you to structure and manage interactions within your multi-agent system.

!!! Note
    The specific parameters or method names for the primitives may vary slightly by SDK language (e.g., `sub_agents` in Python, `subAgents` in Java). Refer to the language-specific API documentation for details.

### 1.1. Agent Hierarchy (Parent agent, Sub Agents) { #agent-hierarchy-parent-agent-sub-agents }

The foundation for structuring multi-agent systems is the parent-child relationship defined in `BaseAgent`.

* **Establishing Hierarchy:** You create a tree structure by passing a list of agent instances to the `sub_agents` argument when initializing a parent agent. ADK automatically sets the `parent_agent` attribute on each child agent during initialization.
* **Single Parent Rule:** An agent instance can only be added as a sub-agent once. Attempting to assign a second parent will result in a `ValueError`.
* **Importance:** This hierarchy defines the scope for [Workflow Agents](#workflow-agents-as-orchestrators) and influences the potential targets for LLM-Driven Delegation. You can navigate the hierarchy using `agent.parent_agent` or find descendants using `agent.find_agent(name)`.

=== "Python"

    ```python
    # Conceptual Example: Defining Hierarchy
    from google.adk.agents import LlmAgent, BaseAgent


    # Define individual agents
    greeter = LlmAgent(name="Greeter", model="gemini-2.0-flash")
    task_doer = BaseAgent(name="TaskExecutor") # Custom non-LLM agent


    # Create parent agent and assign children via sub_agents
    coordinator = LlmAgent(
        name="Coordinator",
        model="gemini-2.0-flash",
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
    const greeter = new LlmAgent({name: 'Greeter', model: 'gemini-2.5-flash'});
    const taskDoer = new TaskExecutorAgent({name: 'TaskExecutor'}); // Custom non-LLM agent

    // Create parent agent and assign children via subAgents
    const coordinator = new LlmAgent({
        name: 'Coordinator',
        model: 'gemini-2.5-flash',
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
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:hierarchy"
    ```

=== "Java"

    ```java
    // Conceptual Example: Defining Hierarchy
    import com.google.adk.agents.SequentialAgent;
    import com.google.adk.agents.LlmAgent;


    // Define individual agents
    LlmAgent greeter = LlmAgent.builder().name("Greeter").model("gemini-2.0-flash").build();
    SequentialAgent taskDoer = SequentialAgent.builder().name("TaskExecutor").subAgents(...).build(); // Sequential Agent


    // Create parent agent and assign sub_agents
    LlmAgent coordinator = LlmAgent.builder()
        .name("Coordinator")
        .model("gemini-2.0-flash")
        .description("I coordinate greetings and tasks")
        .subAgents(greeter, taskDoer) // Assign sub_agents here
        .build();


    // Framework automatically sets:
    // assert greeter.parentAgent().equals(coordinator);
    // assert taskDoer.parentAgent().equals(coordinator);
    ```

### 1.2. Workflow Agents as Orchestrators { #workflow-agents-as-orchestrators }

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
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/agent/workflowagents/sequentialagent"
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
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/agent/workflowagents/parallelagent"
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
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/agent/workflowagents/loopagent"
        "google.golang.org/adk/session"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:loop-with-condition"
    ```

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

### 1.3. Interaction & Communication Mechanisms { #interaction-communication-mechanisms }

Agents within a system often need to exchange data or trigger actions in one another. ADK facilitates this through:

#### a) Shared Session State (`session.state`)

The most fundamental way for agents operating within the same invocation (and thus sharing the same [`Session`](/adk-docs/sessions/session/) object via the `InvocationContext`) to communicate passively.

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
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/agent/workflowagents/sequentialagent"
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

#### b) LLM-Driven Delegation (Agent Transfer)

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
        model="gemini-2.0-flash",
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
        model: 'gemini-2.5-flash',
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
        "google.golang.org/adk/agent/llmagent"
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
        .model("gemini-2.0-flash") // Or your desired model
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

#### c) Explicit Invocation (`AgentTool`)

Allows an [`LlmAgent`](llm-agents.md) to treat another `BaseAgent` instance as a callable function or 
[Tool](/adk-docs/tools-custom/).

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
        model="gemini-2.0-flash",
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
        model: 'gemini-2.5-flash',
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
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/model"
        "google.golang.org/adk/session"
        "google.golang.org/adk/tool"
        "google.golang.org/adk/tool/agenttool"
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
            .model("gemini-2.0-flash")
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

These primitives provide the flexibility to design multi-agent interactions ranging from tightly coupled sequential workflows to dynamic, LLM-driven delegation networks.

## 2. Common Multi-Agent Patterns using ADK Primitives { #common-multi-agent-patterns-using-adk-primitives }

By combining ADK's composition primitives, you can implement various established patterns for multi-agent collaboration.

### Coordinator/Dispatcher Pattern

* **Structure:** A central [`LlmAgent`](llm-agents.md) (Coordinator) manages several specialized `sub_agents`.
* **Goal:** Route incoming requests to the appropriate specialist agent.
* **ADK Primitives Used:**
    * **Hierarchy:** Coordinator has specialists listed in `sub_agents`.
    * **Interaction:** Primarily uses **LLM-Driven Delegation** (requires clear `description`s on sub-agents and appropriate `instruction` on Coordinator) or **Explicit Invocation (`AgentTool`)** (Coordinator includes `AgentTool`-wrapped specialists in its `tools`).

=== "Python"

    ```python
    # Conceptual Code: Coordinator using LLM Transfer
    from google.adk.agents import LlmAgent


    billing_agent = LlmAgent(name="Billing", description="Handles billing inquiries.")
    support_agent = LlmAgent(name="Support", description="Handles technical support requests.")


    coordinator = LlmAgent(
        name="HelpDeskCoordinator",
        model="gemini-2.0-flash",
        instruction="Route user requests: Use Billing agent for payment issues, Support agent for technical problems.",
        description="Main help desk router.",
        # allow_transfer=True is often implicit with sub_agents in AutoFlow
        sub_agents=[billing_agent, support_agent]
    )
    # User asks "My payment failed" -> Coordinator's LLM should call transfer_to_agent(agent_name='Billing')
    # User asks "I can't log in" -> Coordinator's LLM should call transfer_to_agent(agent_name='Support')
    ```

=== "Typescript"

    ```typescript
    // Conceptual Code: Coordinator using LLM Transfer
    import { LlmAgent } from '@google/adk';

    const billingAgent = new LlmAgent({name: 'Billing', description: 'Handles billing inquiries.'});
    const supportAgent = new LlmAgent({name: 'Support', description: 'Handles technical support requests.'});

    const coordinator = new LlmAgent({
        name: 'HelpDeskCoordinator',
        model: 'gemini-2.5-flash',
        instruction: 'Route user requests: Use Billing agent for payment issues, Support agent for technical problems.',
        description: 'Main help desk router.',
        // allowTransfer=true is often implicit with subAgents in AutoFlow
        subAgents: [billingAgent, supportAgent]
    });
    // User asks "My payment failed" -> Coordinator's LLM should call {functionCall: {name: 'transfer_to_agent', args: {agent_name: 'Billing'}}}
    // User asks "I can't log in" -> Coordinator's LLM should call {functionCall: {name: 'transfer_to_agent', args: {agent_name: 'Support'}}}
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:coordinator-pattern"
    ```

=== "Java"

    ```java
    // Conceptual Code: Coordinator using LLM Transfer
    import com.google.adk.agents.LlmAgent;

    LlmAgent billingAgent = LlmAgent.builder()
        .name("Billing")
        .description("Handles billing inquiries and payment issues.")
        .build();

    LlmAgent supportAgent = LlmAgent.builder()
        .name("Support")
        .description("Handles technical support requests and login problems.")
        .build();

    LlmAgent coordinator = LlmAgent.builder()
        .name("HelpDeskCoordinator")
        .model("gemini-2.0-flash")
        .instruction("Route user requests: Use Billing agent for payment issues, Support agent for technical problems.")
        .description("Main help desk router.")
        .subAgents(billingAgent, supportAgent)
        // Agent transfer is implicit with sub agents in the Autoflow, unless specified
        // using .disallowTransferToParent or disallowTransferToPeers
        .build();

    // User asks "My payment failed" -> Coordinator's LLM should call
    // transferToAgent(agentName='Billing')
    // User asks "I can't log in" -> Coordinator's LLM should call
    // transferToAgent(agentName='Support')
    ```

### Sequential Pipeline Pattern

* **Structure:** A [`SequentialAgent`](workflow-agents/sequential-agents.md) contains `sub_agents` executed in a fixed order.
* **Goal:** Implement a multistep process where the output of one-step feeds into the next.
* **ADK Primitives Used:**
    * **Workflow:** `SequentialAgent` defines the order.
    * **Communication:** Primarily uses **Shared Session State**. Earlier agents write results (often via `output_key`), later agents read those results from `context.state`.

=== "Python"

    ```python
    # Conceptual Code: Sequential Data Pipeline
    from google.adk.agents import SequentialAgent, LlmAgent


    validator = LlmAgent(name="ValidateInput", instruction="Validate the input.", output_key="validation_status")
    processor = LlmAgent(name="ProcessData", instruction="Process data if {validation_status} is 'valid'.", output_key="result")
    reporter = LlmAgent(name="ReportResult", instruction="Report the result from {result}.")


    data_pipeline = SequentialAgent(
        name="DataPipeline",
        sub_agents=[validator, processor, reporter]
    )
    # validator runs -> saves to state['validation_status']
    # processor runs -> reads state['validation_status'], saves to state['result']
    # reporter runs -> reads state['result']
    ```

=== "Typescript"

    ```typescript
    // Conceptual Code: Sequential Data Pipeline
    import { SequentialAgent, LlmAgent } from '@google/adk';

    const validator = new LlmAgent({name: 'ValidateInput', instruction: 'Validate the input.', outputKey: 'validation_status'});
    const processor = new LlmAgent({name: 'ProcessData', instruction: 'Process data if {validation_status} is "valid".', outputKey: 'result'});
    const reporter = new LlmAgent({name: 'ReportResult', instruction: 'Report the result from {result}.'});

    const dataPipeline = new SequentialAgent({
        name: 'DataPipeline',
        subAgents: [validator, processor, reporter]
    });
    // validator runs -> saves to state['validation_status']
    // processor runs -> reads state['validation_status'], saves to state['result']
    // reporter runs -> reads state['result']
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/agent/workflowagents/sequentialagent"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:sequential-pipeline-pattern"
    ```

=== "Java"

    ```java
    // Conceptual Code: Sequential Data Pipeline
    import com.google.adk.agents.SequentialAgent;


    LlmAgent validator = LlmAgent.builder()
        .name("ValidateInput")
        .instruction("Validate the input")
        .outputKey("validation_status") // Saves its main text output to session.state["validation_status"]
        .build();


    LlmAgent processor = LlmAgent.builder()
        .name("ProcessData")
        .instruction("Process data if {validation_status} is 'valid'")
        .outputKey("result") // Saves its main text output to session.state["result"]
        .build();


    LlmAgent reporter = LlmAgent.builder()
        .name("ReportResult")
        .instruction("Report the result from {result}")
        .build();


    SequentialAgent dataPipeline = SequentialAgent.builder()
        .name("DataPipeline")
        .subAgents(validator, processor, reporter)
        .build();


    // validator runs -> saves to state['validation_status']
    // processor runs -> reads state['validation_status'], saves to state['result']
    // reporter runs -> reads state['result']
    ```

### Parallel Fan-Out/Gather Pattern

* **Structure:** A [`ParallelAgent`](workflow-agents/parallel-agents.md) runs multiple `sub_agents` concurrently, often followed by a later agent (in a `SequentialAgent`) that aggregates results.
* **Goal:** Execute independent tasks simultaneously to reduce latency, then combine their outputs.
* **ADK Primitives Used:**
    * **Workflow:** `ParallelAgent` for concurrent execution (Fan-Out). Often nested within a `SequentialAgent` to handle the subsequent aggregation step (Gather).
    * **Communication:** Sub-agents write results to distinct keys in **Shared Session State**. The subsequent "Gather" agent reads multiple state keys.

=== "Python"

    ```python
    # Conceptual Code: Parallel Information Gathering
    from google.adk.agents import SequentialAgent, ParallelAgent, LlmAgent


    fetch_api1 = LlmAgent(name="API1Fetcher", instruction="Fetch data from API 1.", output_key="api1_data")
    fetch_api2 = LlmAgent(name="API2Fetcher", instruction="Fetch data from API 2.", output_key="api2_data")


    gather_concurrently = ParallelAgent(
        name="ConcurrentFetch",
        sub_agents=[fetch_api1, fetch_api2]
    )


    synthesizer = LlmAgent(
        name="Synthesizer",
        instruction="Combine results from {api1_data} and {api2_data}."
    )


    overall_workflow = SequentialAgent(
        name="FetchAndSynthesize",
        sub_agents=[gather_concurrently, synthesizer] # Run parallel fetch, then synthesize
    )
    # fetch_api1 and fetch_api2 run concurrently, saving to state.
    # synthesizer runs afterwards, reading state['api1_data'] and state['api2_data'].
    ```

=== "Typescript"

    ```typescript
    // Conceptual Code: Parallel Information Gathering
    import { SequentialAgent, ParallelAgent, LlmAgent } from '@google/adk';

    const fetchApi1 = new LlmAgent({name: 'API1Fetcher', instruction: 'Fetch data from API 1.', outputKey: 'api1_data'});
    const fetchApi2 = new LlmAgent({name: 'API2Fetcher', instruction: 'Fetch data from API 2.', outputKey: 'api2_data'});

    const gatherConcurrently = new ParallelAgent({
        name: 'ConcurrentFetch',
        subAgents: [fetchApi1, fetchApi2]
    });

    const synthesizer = new LlmAgent({
        name: 'Synthesizer',
        instruction: 'Combine results from {api1_data} and {api2_data}.'
    });

    const overallWorkflow = new SequentialAgent({
        name: 'FetchAndSynthesize',
        subAgents: [gatherConcurrently, synthesizer] // Run parallel fetch, then synthesize
    });
    // fetchApi1 and fetchApi2 run concurrently, saving to state.
    // synthesizer runs afterwards, reading state['api1_data'] and state['api2_data'].
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/agent/workflowagents/parallelagent"
        "google.golang.org/adk/agent/workflowagents/sequentialagent"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:parallel-gather-pattern"
    ```

=== "Java"

    ```java
    // Conceptual Code: Parallel Information Gathering
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.ParallelAgent;
    import com.google.adk.agents.SequentialAgent;

    LlmAgent fetchApi1 = LlmAgent.builder()
        .name("API1Fetcher")
        .instruction("Fetch data from API 1.")
        .outputKey("api1_data")
        .build();

    LlmAgent fetchApi2 = LlmAgent.builder()
        .name("API2Fetcher")
        .instruction("Fetch data from API 2.")
        .outputKey("api2_data")
        .build();

    ParallelAgent gatherConcurrently = ParallelAgent.builder()
        .name("ConcurrentFetcher")
        .subAgents(fetchApi2, fetchApi1)
        .build();

    LlmAgent synthesizer = LlmAgent.builder()
        .name("Synthesizer")
        .instruction("Combine results from {api1_data} and {api2_data}.")
        .build();

    SequentialAgent overallWorfklow = SequentialAgent.builder()
        .name("FetchAndSynthesize") // Run parallel fetch, then synthesize
        .subAgents(gatherConcurrently, synthesizer)
        .build();

    // fetch_api1 and fetch_api2 run concurrently, saving to state.
    // synthesizer runs afterwards, reading state['api1_data'] and state['api2_data'].
    ```

### Hierarchical Task Decomposition

* **Structure:** A multi-level tree of agents where higher-level agents break down complex goals and delegate sub-tasks to lower-level agents.
* **Goal:** Solve complex problems by recursively breaking them down into simpler, executable steps.
* **ADK Primitives Used:**
    * **Hierarchy:** Multi-level `parent_agent`/`sub_agents` structure.
    * **Interaction:** Primarily **LLM-Driven Delegation** or **Explicit Invocation (`AgentTool`)** used by parent agents to assign tasks to subagents. Results are returned up the hierarchy (via tool responses or state).

=== "Python"

    ```python
    # Conceptual Code: Hierarchical Research Task
    from google.adk.agents import LlmAgent
    from google.adk.tools import agent_tool


    # Low-level tool-like agents
    web_searcher = LlmAgent(name="WebSearch", description="Performs web searches for facts.")
    summarizer = LlmAgent(name="Summarizer", description="Summarizes text.")


    # Mid-level agent combining tools
    research_assistant = LlmAgent(
        name="ResearchAssistant",
        model="gemini-2.0-flash",
        description="Finds and summarizes information on a topic.",
        tools=[agent_tool.AgentTool(agent=web_searcher), agent_tool.AgentTool(agent=summarizer)]
    )


    # High-level agent delegating research
    report_writer = LlmAgent(
        name="ReportWriter",
        model="gemini-2.0-flash",
        instruction="Write a report on topic X. Use the ResearchAssistant to gather information.",
        tools=[agent_tool.AgentTool(agent=research_assistant)]
        # Alternatively, could use LLM Transfer if research_assistant is a sub_agent
    )
    # User interacts with ReportWriter.
    # ReportWriter calls ResearchAssistant tool.
    # ResearchAssistant calls WebSearch and Summarizer tools.
    # Results flow back up.
    ```

=== "Typescript"

    ```typescript
    // Conceptual Code: Hierarchical Research Task
    import { LlmAgent, AgentTool } from '@google/adk';

    // Low-level tool-like agents
    const webSearcher = new LlmAgent({name: 'WebSearch', description: 'Performs web searches for facts.'});
    const summarizer = new LlmAgent({name: 'Summarizer', description: 'Summarizes text.'});

    // Mid-level agent combining tools
    const researchAssistant = new LlmAgent({
        name: 'ResearchAssistant',
        model: 'gemini-2.5-flash',
        description: 'Finds and summarizes information on a topic.',
        tools: [new AgentTool({agent: webSearcher}), new AgentTool({agent: summarizer})]
    });

    // High-level agent delegating research
    const reportWriter = new LlmAgent({
        name: 'ReportWriter',
        model: 'gemini-2.5-flash',
        instruction: 'Write a report on topic X. Use the ResearchAssistant to gather information.',
        tools: [new AgentTool({agent: researchAssistant})]
        // Alternatively, could use LLM Transfer if researchAssistant is a subAgent
    });
    // User interacts with ReportWriter.
    // ReportWriter calls ResearchAssistant tool.
    // ResearchAssistant calls WebSearch and Summarizer tools.
    // Results flow back up.
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/tool"
        "google.golang.org/adk/tool/agenttool"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:hierarchical-pattern"
    ```

=== "Java"

    ```java
    // Conceptual Code: Hierarchical Research Task
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.tools.AgentTool;


    // Low-level tool-like agents
    LlmAgent webSearcher = LlmAgent.builder()
        .name("WebSearch")
        .description("Performs web searches for facts.")
        .build();


    LlmAgent summarizer = LlmAgent.builder()
        .name("Summarizer")
        .description("Summarizes text.")
        .build();


    // Mid-level agent combining tools
    LlmAgent researchAssistant = LlmAgent.builder()
        .name("ResearchAssistant")
        .model("gemini-2.0-flash")
        .description("Finds and summarizes information on a topic.")
        .tools(AgentTool.create(webSearcher), AgentTool.create(summarizer))
        .build();


    // High-level agent delegating research
    LlmAgent reportWriter = LlmAgent.builder()
        .name("ReportWriter")
        .model("gemini-2.0-flash")
        .instruction("Write a report on topic X. Use the ResearchAssistant to gather information.")
        .tools(AgentTool.create(researchAssistant))
        // Alternatively, could use LLM Transfer if research_assistant is a subAgent
        .build();


    // User interacts with ReportWriter.
    // ReportWriter calls ResearchAssistant tool.
    // ResearchAssistant calls WebSearch and Summarizer tools.
    // Results flow back up.
    ```

### Review/Critique Pattern (Generator-Critic)

* **Structure:** Typically involves two agents within a [`SequentialAgent`](workflow-agents/sequential-agents.md): a Generator and a Critic/Reviewer.
* **Goal:** Improve the quality or validity of generated output by having a dedicated agent review it.
* **ADK Primitives Used:**
    * **Workflow:** `SequentialAgent` ensures generation happens before review.
    * **Communication:** **Shared Session State** (Generator uses `output_key` to save output; Reviewer reads that state key). The Reviewer might save its feedback to another state key for subsequent steps.

=== "Python"

    ```python
    # Conceptual Code: Generator-Critic
    from google.adk.agents import SequentialAgent, LlmAgent


    generator = LlmAgent(
        name="DraftWriter",
        instruction="Write a short paragraph about subject X.",
        output_key="draft_text"
    )


    reviewer = LlmAgent(
        name="FactChecker",
        instruction="Review the text in {draft_text} for factual accuracy. Output 'valid' or 'invalid' with reasons.",
        output_key="review_status"
    )


    # Optional: Further steps based on review_status


    review_pipeline = SequentialAgent(
        name="WriteAndReview",
        sub_agents=[generator, reviewer]
    )
    # generator runs -> saves draft to state['draft_text']
    # reviewer runs -> reads state['draft_text'], saves status to state['review_status']
    ```

=== "Typescript"

    ```typescript
    // Conceptual Code: Generator-Critic
    import { SequentialAgent, LlmAgent } from '@google/adk';

    const generator = new LlmAgent({
        name: 'DraftWriter',
        instruction: 'Write a short paragraph about subject X.',
        outputKey: 'draft_text'
    });

    const reviewer = new LlmAgent({
        name: 'FactChecker',
        instruction: 'Review the text in {draft_text} for factual accuracy. Output "valid" or "invalid" with reasons.',
        outputKey: 'review_status'
    });

    // Optional: Further steps based on review_status

    const reviewPipeline = new SequentialAgent({
        name: 'WriteAndReview',
        subAgents: [generator, reviewer]
    });
    // generator runs -> saves draft to state['draft_text']
    // reviewer runs -> reads state['draft_text'], saves status to state['review_status']
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/agent/workflowagents/sequentialagent"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:generator-critic-pattern"
    ```

=== "Java"

    ```java
    // Conceptual Code: Generator-Critic
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.SequentialAgent;


    LlmAgent generator = LlmAgent.builder()
        .name("DraftWriter")
        .instruction("Write a short paragraph about subject X.")
        .outputKey("draft_text")
        .build();


    LlmAgent reviewer = LlmAgent.builder()
        .name("FactChecker")
        .instruction("Review the text in {draft_text} for factual accuracy. Output 'valid' or 'invalid' with reasons.")
        .outputKey("review_status")
        .build();


    // Optional: Further steps based on review_status


    SequentialAgent reviewPipeline = SequentialAgent.builder()
        .name("WriteAndReview")
        .subAgents(generator, reviewer)
        .build();


    // generator runs -> saves draft to state['draft_text']
    // reviewer runs -> reads state['draft_text'], saves status to state['review_status']
    ```

### Iterative Refinement Pattern

* **Structure:** Uses a [`LoopAgent`](workflow-agents/loop-agents.md) containing one or more agents that work on a task over multiple iterations.
* **Goal:** Progressively improve a result (e.g., code, text, plan) stored in the session state until a quality threshold is met or a maximum number of iterations is reached.
* **ADK Primitives Used:**
    * **Workflow:** `LoopAgent` manages the repetition.
    * **Communication:** **Shared Session State** is essential for agents to read the previous iteration's output and save the refined version.
    * **Termination:** The loop typically ends based on `max_iterations` or a dedicated checking agent setting `escalate=True` in the `Event Actions` when the result is satisfactory.

=== "Python"

    ```python
    # Conceptual Code: Iterative Code Refinement
    from google.adk.agents import LoopAgent, LlmAgent, BaseAgent
    from google.adk.events import Event, EventActions
    from google.adk.agents.invocation_context import InvocationContext
    from typing import AsyncGenerator


    # Agent to generate/refine code based on state['current_code'] and state['requirements']
    code_refiner = LlmAgent(
        name="CodeRefiner",
        instruction="Read state['current_code'] (if exists) and state['requirements']. Generate/refine Python code to meet requirements. Save to state['current_code'].",
        output_key="current_code" # Overwrites previous code in state
    )


    # Agent to check if the code meets quality standards
    quality_checker = LlmAgent(
        name="QualityChecker",
        instruction="Evaluate the code in state['current_code'] against state['requirements']. Output 'pass' or 'fail'.",
        output_key="quality_status"
    )


    # Custom agent to check the status and escalate if 'pass'
    class CheckStatusAndEscalate(BaseAgent):
        async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
            status = ctx.session.state.get("quality_status", "fail")
            should_stop = (status == "pass")
            yield Event(author=self.name, actions=EventActions(escalate=should_stop))


    refinement_loop = LoopAgent(
        name="CodeRefinementLoop",
        max_iterations=5,
        sub_agents=[code_refiner, quality_checker, CheckStatusAndEscalate(name="StopChecker")]
    )
    # Loop runs: Refiner -> Checker -> StopChecker
    # State['current_code'] is updated each iteration.
    # Loop stops if QualityChecker outputs 'pass' (leading to StopChecker escalating) or after 5 iterations.
    ```

=== "Typescript"

    ```typescript
    // Conceptual Code: Iterative Code Refinement
    import { LoopAgent, LlmAgent, BaseAgent, InvocationContext } from '@google/adk';
    import type { Event, createEvent, createEventActions } from '@google/genai';

    // Agent to generate/refine code based on state['current_code'] and state['requirements']
    const codeRefiner = new LlmAgent({
        name: 'CodeRefiner',
        instruction: 'Read state["current_code"] (if exists) and state["requirements"]. Generate/refine Typescript code to meet requirements. Save to state["current_code"].',
        outputKey: 'current_code' // Overwrites previous code in state
    });

    // Agent to check if the code meets quality standards
    const qualityChecker = new LlmAgent({
        name: 'QualityChecker',
        instruction: 'Evaluate the code in state["current_code"] against state["requirements"]. Output "pass" or "fail".',
        outputKey: 'quality_status'
    });

    // Custom agent to check the status and escalate if 'pass'
    class CheckStatusAndEscalate extends BaseAgent {
        async *runAsyncImpl(ctx: InvocationContext): AsyncGenerator<Event> {
            const status = ctx.session.state.quality_status;
            const shouldStop = status === 'pass';
            if (shouldStop) {
                yield createEvent({
                    author: 'StopChecker',
                    actions: createEventActions(),
                });
            }
        }

        async *runLiveImpl(ctx: InvocationContext): AsyncGenerator<Event> {
            // This agent doesn't have a live implementation
            yield createEvent({ author: 'StopChecker' });
        }
    }

    // Loop runs: Refiner -> Checker -> StopChecker
    // State['current_code'] is updated each iteration.
    // Loop stops if QualityChecker outputs 'pass' (leading to StopChecker escalating) or after 5 iterations.
    const refinementLoop = new LoopAgent({
        name: 'CodeRefinementLoop',
        maxIterations: 5,
        subAgents: [codeRefiner, qualityChecker, new CheckStatusAndEscalate({name: 'StopChecker'})]
    });
    ```

=== "Go"

    ```go
    import (
        "iter"
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/agent/workflowagents/loopagent"
        "google.golang.org/adk/session"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:iterative-refinement-pattern"
    ```

=== "Java"

    ```java
    // Conceptual Code: Iterative Code Refinement
    import com.google.adk.agents.BaseAgent;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.LoopAgent;
    import com.google.adk.events.Event;
    import com.google.adk.events.EventActions;
    import com.google.adk.agents.InvocationContext;
    import io.reactivex.rxjava3.core.Flowable;
    import java.util.List;


    // Agent to generate/refine code based on state['current_code'] and state['requirements']
    LlmAgent codeRefiner = LlmAgent.builder()
        .name("CodeRefiner")
        .instruction("Read state['current_code'] (if exists) and state['requirements']. Generate/refine Java code to meet requirements. Save to state['current_code'].")
        .outputKey("current_code") // Overwrites previous code in state
        .build();


    // Agent to check if the code meets quality standards
    LlmAgent qualityChecker = LlmAgent.builder()
        .name("QualityChecker")
        .instruction("Evaluate the code in state['current_code'] against state['requirements']. Output 'pass' or 'fail'.")
        .outputKey("quality_status")
        .build();


    BaseAgent checkStatusAndEscalate = new BaseAgent(
        "StopChecker","Checks quality_status and escalates if 'pass'.", List.of(), null, null) {


      @Override
      protected Flowable<Event> runAsyncImpl(InvocationContext invocationContext) {
        String status = (String) invocationContext.session().state().getOrDefault("quality_status", "fail");
        boolean shouldStop = "pass".equals(status);


        EventActions actions = EventActions.builder().escalate(shouldStop).build();
        Event event = Event.builder()
            .author(this.name())
            .actions(actions)
            .build();
        return Flowable.just(event);
      }
    };


    LoopAgent refinementLoop = LoopAgent.builder()
        .name("CodeRefinementLoop")
        .maxIterations(5)
        .subAgents(codeRefiner, qualityChecker, checkStatusAndEscalate)
        .build();


    // Loop runs: Refiner -> Checker -> StopChecker
    // State['current_code'] is updated each iteration.
    // Loop stops if QualityChecker outputs 'pass' (leading to StopChecker escalating) or after 5
    // iterations.
    ```

### Human-in-the-Loop Pattern

* **Structure:** Integrates human intervention points within an agent workflow.
* **Goal:** Allow for human oversight, approval, correction, or tasks that AI cannot perform.
* **ADK Primitives Used (Conceptual):**
    * **Interaction:** Can be implemented using a custom **Tool** that pauses execution and sends a request to an external system (e.g., a UI, ticketing system) waiting for human input. The tool then returns the human's response to the agent.
    * **Workflow:** Could use **LLM-Driven Delegation** (`transfer_to_agent`) targeting a conceptual "Human Agent" that triggers the external workflow, or use the custom tool within an `LlmAgent`.
    * **State/Callbacks:** State can hold task details for the human; callbacks can manage the interaction flow.
    * **Note:** ADK doesn't have a built-in "Human Agent" type, so this requires custom integration.

=== "Python"

    ```python
    # Conceptual Code: Using a Tool for Human Approval
    from google.adk.agents import LlmAgent, SequentialAgent
    from google.adk.tools import FunctionTool


    # --- Assume external_approval_tool exists ---
    # This tool would:
    # 1. Take details (e.g., request_id, amount, reason).
    # 2. Send these details to a human review system (e.g., via API).
    # 3. Poll or wait for the human response (approved/rejected).
    # 4. Return the human's decision.
    # async def external_approval_tool(amount: float, reason: str) -> str: ...
    approval_tool = FunctionTool(func=external_approval_tool)


    # Agent that prepares the request
    prepare_request = LlmAgent(
        name="PrepareApproval",
        instruction="Prepare the approval request details based on user input. Store amount and reason in state.",
        # ... likely sets state['approval_amount'] and state['approval_reason'] ...
    )


    # Agent that calls the human approval tool
    request_approval = LlmAgent(
        name="RequestHumanApproval",
        instruction="Use the external_approval_tool with amount from state['approval_amount'] and reason from state['approval_reason'].",
        tools=[approval_tool],
        output_key="human_decision"
    )


    # Agent that proceeds based on human decision
    process_decision = LlmAgent(
        name="ProcessDecision",
        instruction="Check {human_decision}. If 'approved', proceed. If 'rejected', inform user."
    )


    approval_workflow = SequentialAgent(
        name="HumanApprovalWorkflow",
        sub_agents=[prepare_request, request_approval, process_decision]
    )
    ```

=== "Typescript"

    ```typescript
    // Conceptual Code: Using a Tool for Human Approval
    import { LlmAgent, SequentialAgent, FunctionTool } from '@google/adk';
    import { z } from 'zod';

    // --- Assume externalApprovalTool exists ---
    // This tool would:
    // 1. Take details (e.g., request_id, amount, reason).
    // 2. Send these details to a human review system (e.g., via API).
    // 3. Poll or wait for the human response (approved/rejected).
    // 4. Return the human's decision.
    async function externalApprovalTool(params: {amount: number, reason: string}): Promise<{decision: string}> {
      // ... implementation to call external system
      return {decision: 'approved'}; // or 'rejected'
    }

    const approvalTool = new FunctionTool({
      name: 'external_approval_tool',
      description: 'Sends a request for human approval.',
      parameters: z.object({
        amount: z.number(),
        reason: z.string(),
      }),
      execute: externalApprovalTool,
    });


    // Agent that prepares the request
    const prepareRequest = new LlmAgent({
        name: 'PrepareApproval',
        instruction: 'Prepare the approval request details based on user input. Store amount and reason in state.',
        // ... likely sets state['approval_amount'] and state['approval_reason'] ...
    });

    // Agent that calls the human approval tool
    const requestApproval = new LlmAgent({
        name: 'RequestHumanApproval',
        instruction: 'Use the external_approval_tool with amount from state["approval_amount"] and reason from state["approval_reason"].',
        tools: [approvalTool],
        outputKey: 'human_decision'
    });

    // Agent that proceeds based on human decision
    const processDecision = new LlmAgent({
        name: 'ProcessDecision',
        instruction: 'Check {human_decision}. If "approved", proceed. If "rejected", inform user.'
    });

    const approvalWorkflow = new SequentialAgent({
        name: 'HumanApprovalWorkflow',
        subAgents: [prepareRequest, requestApproval, processDecision]
    });
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/agent/workflowagents/sequentialagent"
        "google.golang.org/adk/tool"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:human-in-loop-pattern"
    ```

=== "Java"

    ```java
    // Conceptual Code: Using a Tool for Human Approval
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.SequentialAgent;
    import com.google.adk.tools.FunctionTool;


    // --- Assume external_approval_tool exists ---
    // This tool would:
    // 1. Take details (e.g., request_id, amount, reason).
    // 2. Send these details to a human review system (e.g., via API).
    // 3. Poll or wait for the human response (approved/rejected).
    // 4. Return the human's decision.
    // public boolean externalApprovalTool(float amount, String reason) { ... }
    FunctionTool approvalTool = FunctionTool.create(externalApprovalTool);


    // Agent that prepares the request
    LlmAgent prepareRequest = LlmAgent.builder()
        .name("PrepareApproval")
        .instruction("Prepare the approval request details based on user input. Store amount and reason in state.")
        // ... likely sets state['approval_amount'] and state['approval_reason'] ...
        .build();


    // Agent that calls the human approval tool
    LlmAgent requestApproval = LlmAgent.builder()
        .name("RequestHumanApproval")
        .instruction("Use the external_approval_tool with amount from state['approval_amount'] and reason from state['approval_reason'].")
        .tools(approvalTool)
        .outputKey("human_decision")
        .build();


    // Agent that proceeds based on human decision
    LlmAgent processDecision = LlmAgent.builder()
        .name("ProcessDecision")
        .instruction("Check {human_decision}. If 'approved', proceed. If 'rejected', inform user.")
        .build();


    SequentialAgent approvalWorkflow = SequentialAgent.builder()
        .name("HumanApprovalWorkflow")
        .subAgents(prepareRequest, requestApproval, processDecision)
        .build();
    ```

#### Human in the Loop with Policy

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
    const rootAgent = new LlmAgent({
      name: 'weather_time_agent',
      model: 'gemini-2.5-flash',
      description:
          'Agent to answer questions about the time and weather in a city.',
      instruction:
          'You are a helpful agent who can answer user questions about the time and weather in a city.',
      tools: [getWeatherTool],
    });

    class CustomPolicyEngine implements BasePolicyEngine {
      async evaluate(_context: ToolCallPolicyContext): Promise<PolicyCheckResult> {
        // Default permissive implementation
        return Promise.resolve({
          outcome: PolicyOutcome.CONFIRM,
          reason: 'Needs confirmation for tool call',
        });
      }
    }

    const runner = new InMemoryRunner({
        agent: rootAgent,
        appName,
        plugins: [new SecurityPlugin({policyEngine: new CustomPolicyEngine()})]
    });
    ```

    You can find the full code sample [here](https://github.com/google/adk-docs/blob/main/examples/typescript/snippets/agents/workflow-agents/hitl_confirmation_agent.ts).

### Combining Patterns

These patterns provide starting points for structuring your multi-agent systems. You can mix and match them as needed to create the most effective architecture for your specific application.
