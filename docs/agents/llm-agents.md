# Simple agents with LlmAgent

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

The `LlmAgent` class, often aliased simply as `Agent`, is a core component in
ADK, acting as the core part of your agent application. It leverages the power
of a Large Language Model (LLM) or generative AI model for reasoning,
understanding natural language, making decisions, generating responses, and
interacting with tools. Since this type of agent uses an AI model to interpret
instructions and context, the AI model dynamically decides how to proceed, which
tools to use (if any), and what output to provide. As such, the behavior of this
type of agent is non-deterministic and must be built and evaluated with this
behavior in mind.

Building an effective `LlmAgent` involves defining its identity, clearly guiding
its behavior through instructions, and equipping it with the necessary tools and
capabilities.

## Define agent identity and purpose

First, you need to establish what the agent *is* and what it's *for*.

- **`name` (Required):** Every agent needs a unique string identifier. This
  `name` is crucial for internal operations, especially in multi-agent systems
  where agents need to refer to or delegate tasks to each other. Choose a
  descriptive name that reflects the agent's function (e.g.,
  `customer_support_router`, `billing_inquiry_agent`). Avoid reserved names like
  `user`.

- **`description` (Optional, Recommended for Multi-Agent):** Provide a concise
  summary of the agent's capabilities. This description is primarily used by
  *other* LLM agents to determine if they should route a task to this agent.
  Make it specific enough to differentiate it from peers (e.g., "Handles
  inquiries about current billing statements," not just "Billing agent").

- **`model` (Required):** Specify the underlying LLM that will power this
  agent's reasoning. This is a string identifier like `"gemini-flash-latest"`.
  The choice of model impacts the agent's capabilities, cost, and performance.
  See the [Models](/agents/models/) page for available options and
  considerations.

=== "Python"

    ```python
    --8<-- "examples/inline/python/agents/llm-agents/001-define-agent-identity-and-purpose.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/agents/llm-agents/002-define-agent-identity-and-purpose.ts"
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/agents/llm-agents/snippets/main.go:identity"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/agents/llm-agents/003-define-agent-identity-and-purpose.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/agents/llm-agent/CapitalAgent.kt:identity"
    ```

## Guide the agent with instructions

The `instruction` parameter is arguably the most critical for shaping an
`LlmAgent`'s behavior. It's a string (or a function returning a string) that
tells the agent:

- Its core task or goal.
- Its personality or persona (e.g., "You are a helpful assistant," "You are a
  witty pirate").
- Constraints on its behavior (e.g., "Only answer questions about X," "Never
  reveal Y").
- How and when to use its `tools`. You should explain the purpose of each tool
  and the circumstances under which it should be called, supplementing any
  descriptions within the tool itself.
- The desired format for its output (e.g., "Respond in JSON," "Provide a
  bulleted list").

**Tips for effective instructions:**

- **Be Clear and Specific:** Avoid ambiguity. Clearly state the desired actions
  and outcomes.
- **Use Markdown:** Improve readability for complex instructions using headings,
  lists, etc.
- **Provide Examples (Few-Shot):** For complex tasks or specific output formats,
  include examples directly in the instruction.
- **Guide Tool Use:** Don't just list tools; explain *when* and *why* the agent
  should use them.

**Use dynamic state variables:**

- The instruction is a string template, you can use the `{var}` syntax to insert
  dynamic values into the instruction.
- `{var}` is used to insert the value of the state variable named var.
- `{artifact.var}` is used to insert the text content of the artifact named var.
- If the state variable or artifact does not exist, the agent will raise an
  error. If you want to ignore the error, you can append a `?` to the variable
  name as in `{var?}`.

=== "Python"

    ```python
    --8<-- "examples/inline/python/agents/llm-agents/004-guide-the-agent-with-instructions.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/agents/llm-agents/005-guide-the-agent-with-instructions.ts"
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/agents/llm-agents/snippets/main.go:instruction"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/agents/llm-agents/006-guide-the-agent-with-instructions.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/agents/llm-agent/CapitalAgent.kt:instruction"
    ```

!!! note "GlobalInstructionPlugin"

    To apply shared rules or a consistent personality to *all* 
    agents in your system, use `GlobalInstructionPlugin` instead of 
    the deprecated `global_instruction` parameter.

## Equip the agent with tools

Tools give your `LlmAgent` capabilities beyond the LLM's built-in knowledge or
reasoning. They allow the agent to interact with the outside world, perform
calculations, fetch real-time data, or execute specific actions.

- **`tools` (Optional):** Provide a list of tools the agent can use. Each item
  in the list can be:
    - A native function or method (wrapped as a `FunctionTool`). Python ADK
      automatically wraps the native function into a `FunctionTool` whereas, you
      must explicitly wrap your Java methods using `FunctionTool.create(...)`.
      In Kotlin, you can use the `@Tool` annotation to automatically generate a
      `FunctionTool` at compile-time.
    - An instance of a class inheriting from `BaseTool`.
    - An instance of another agent (`AgentTool`, enabling agent-to-agent
      delegation - see [Custom agent
      workflows](/agents/custom-agents/#delegation)).

The LLM uses the function/tool names, descriptions (from docstrings or the
`description` field), and parameter schemas to decide which tool to call based
on the conversation and its instructions.

=== "Python"

    ```python
    --8<-- "examples/inline/python/agents/llm-agents/007-equip-the-agent-with-tools.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/agents/llm-agents/008-equip-the-agent-with-tools.ts"
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/agents/llm-agents/snippets/main.go:tool_example"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/agents/llm-agents/009-equip-the-agent-with-tools.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/inline/kotlin/agents/llm-agents/010-equip-the-agent-with-tools.kt"
    ```

Learn more about Tools in [Custom Tools](/tools-custom/).

## Advanced configuration and control

Beyond the core parameters, `LlmAgent` offers several options for finer control:

### Fine-tune AI model operation

You can adjust how the underlying AI model generates responses using
`generate_content_config`.

- **`generate_content_config` (Optional):** Pass an instance of
  [`google.genai.types.GenerateContentConfig`](https://googleapis.github.io/python-genai/genai.html#genai.types.GenerateContentConfig)
  to control parameters like `temperature` (randomness), `max_output_tokens`
  (response length), `top_p`, `top_k`, and safety settings.

=== "Python"

    ```python
    --8<-- "examples/inline/python/agents/llm-agents/011-fine-tune-ai-model-operation.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/agents/llm-agents/012-fine-tune-ai-model-operation.ts"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/agents/llm-agents/013-fine-tune-ai-model-operation.go.txt"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/agents/llm-agents/014-fine-tune-ai-model-operation.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/agents/llm-agent/CapitalAgent.kt:gen_config"
    ```

### Configure a default model

<div class="language-support-tag" title="">
   <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.22.0</span>
</div>

You can set a system-wide default model for all `LlmAgent` instances using the
`set_default_model` class method. If you do not specify a model when creating an
agent, it falls back to ADK's built-in default model. This setting helps you
avoid redundant model specifications and easily change the model for all agents
at once.

=== "Python"

    ```python
    --8<-- "examples/inline/python/agents/llm-agents/015-configure-a-default-model.py"
    ```

### Structure data input and output {#data-handling}

For scenarios requiring structured data exchange with an `LLM Agent`, the ADK
provides mechanisms to define expected input and desired output formats using
schema definitions.

- **`input_schema` (Optional):** Define a schema representing the expected input
  structure. If set, the user message content passed to this agent *must* be a
  JSON string conforming to this schema. Your instructions should guide the user
  or preceding agent accordingly.

- **`output_schema` (Optional):** Define a schema representing the desired
  output structure. If set, the agent's final response *must* be a JSON string
  conforming to this schema.

!!! warning "Warning: Using `output_schema` with `tools`"

    Using `output_schema` with `tools` in the same LLM request is only supported
    by specific models, including [Gemini
    3.0](https://ai.google.dev/gemini-api/docs/function-calling?example=meeting#structured-output).
    For other models, ADK falls back to a [`set_model_response` function
    tool](https://github.com/google/adk-python/blob/main/src/google/adk/flows/llm_flows/_output_schema_processor.py)
    to collect the structured output, which may not work reliably. In such
    cases, consider using sub-agents that handle output formatting separately.

- **`output_key` (Optional):** Provide a string key. If set, the text content of
  the agent's *final* response will be automatically saved to the session's
  state dictionary under this key. This is useful for passing results between
  agents or steps in a workflow.
    - In Python, this might look like: `session.state[output_key] =
      agent_response_text`
    - In Java: `session.state().put(outputKey, agentResponseText)`
    - In Golang, within a callback handler: `ctx.State().Set(output_key,
      agentResponseText)`

    When `output_schema` is also set, the *parsed* response is stored instead of
    the text: a `dict` in Python, and a `Map` in Java and Kotlin.

!!! note "Schema validation in Java and Kotlin"

    Java and Kotlin check the response against the *structure* of the schema —
    `type`, `required`, `nullable`, `anyOf` and `items` (see
    [`SchemaUtils`](https://github.com/google/adk-kotlin/blob/v0.8.0/core/src/commonMain/kotlin/com/google/adk/kt/SchemaUtils.kt)).
    Constraint fields such as `pattern`, `minLength` and `minimum` are sent to
    the model as part of the schema, but ADK does not re-check them, so the
    model decides whether to honor them. Python validates against a Pydantic
    model, which does enforce the constraints declared on it.

    Java and Kotlin accept only a top-level object schema; a top-level array or
    primitive fails validation. Python also supports list and primitive output
    schemas.

    If the response fails validation, ADK logs the error and stores the raw
    response string under `output_key` instead of the parsed object (see
    [`LlmAgent`](https://github.com/google/adk-kotlin/blob/v0.8.0/core/src/commonMain/kotlin/com/google/adk/kt/agents/LlmAgent.kt)).

=== "Python"

    The input and output schema is typically a `Pydantic` BaseModel.

    ```python
    --8<-- "examples/inline/python/agents/llm-agents/016-structure-data-input-and-output-data-han.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/agents/llm-agents/017-structure-data-input-and-output-data-han.ts"
    ```

=== "Go"

    The input and output schema is a `google.genai.types.Schema` object.

    ```go
    --8<-- "examples/go/snippets/agents/llm-agents/snippets/main.go:schema_example"
    ```

=== "Java"

     The input and output schema is a `google.genai.types.Schema` object.

    ```java
    --8<-- "examples/inline/java/agents/llm-agents/018-structure-data-input-and-output-data-han.java"
    ```

=== "Kotlin"

    The input and output schema is ADK's own `com.google.adk.kt.types.Schema`,
    not the same-named type in the GenAI SDK. Starting with ADK Kotlin v0.8.0,
    the JSON schema includes constraints for the following fields: `pattern`,
    `minLength`, `maxLength`, `minimum`, `maximum`, `minItems`, `maxItems`,
    `format`, `nullable`, `default`, `anyOf` and `title`.

    ```kotlin
    --8<-- "examples/kotlin/snippets/agents/llm-agent/CapitalAgent.kt:schema_example"
    ```

    The `format` field accepts only the values the model allows for the field's type. For
    the accepted values, see the Gemini [`Schema`
    reference](https://ai.google.dev/api/caching#Schema).

    The `default` field must contain a JSON-native value. ADK's own `Json` serializes one,
    but a hand-rolled serializer without a contextual `Any` serializer does not.

### Manage agent context

Control whether the agent receives the prior conversation history.

- **`include_contents` (Optional, Default: `'default'`):** Determines if the
  `contents` (history) are sent to the LLM.
    - `'default'`: The agent receives the relevant conversation history.
    - `'none'`: The agent receives no prior `contents`. It operates based solely
      on its current instruction and any input provided in the *current* turn
      (useful for stateless tasks or enforcing specific contexts).

=== "Python"

    ```python
    --8<-- "examples/inline/python/agents/llm-agents/019-manage-agent-context.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/agents/llm-agents/020-manage-agent-context.ts"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/agents/llm-agents/021-manage-agent-context.go.txt"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/agents/llm-agents/022-manage-agent-context.java"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/agents/llm-agent/CapitalAgent.kt:include_contents"
    ```

!!! note "Go v2.0.0: agent execution modes"

    ADK Go v2.0.0 introduces an explicit `Mode` field on `llmagent.Config` that
    controls how the agent runs when used inside a graph-based or dynamic
    workflow. Three modes are available:

    - **`ModeChat`** (default for an agent used as a sub-agent): The agent
      participates in a multi-turn conversation with the user and is reachable
      from peer agents via `transfer_to_agent`.
    - **`ModeSingleTurn`** (default for an agent used as a node in a workflow):
      The agent completes its task in a single turn without chatting with the
      user.
    - **`ModeTask`**: A task agent that chats with the user to accomplish a task
      — in contrast to `ModeSingleTurn`, it can interact with the user across
      turns to complete the work.

    When you wrap an `llmagent` with `workflow.NewAgentNode`, the workflow
    engine automatically sets the mode to `ModeSingleTurn` if no mode is
    specified — equivalent to Python's `mode="single_turn"` on an agent used as
    a workflow node. For more information on composing agents in graph-based
    workflows, see [Graph-based agent workflows](/graphs/).

### Configure a planner

<div class="language-support-tag" title="">
   <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span>
</div>

**`planner` (Optional):** Assign a `BasePlanner` instance to enable multi-step
reasoning and planning before execution. There are two main planners:

- **`BuiltInPlanner`:** Leverages the model's built-in planning capabilities
  (e.g., Gemini's thinking feature). See [Gemini
  Thinking](https://ai.google.dev/gemini-api/docs/thinking) for details and
  examples.

    Here, the `thinking_budget` parameter guides the model on the number of
    thinking tokens to use when generating a response. The `include_thoughts`
    parameter controls whether the model should include its raw thoughts and
    internal reasoning process in the response.

    ```python
    --8<-- "examples/inline/python/agents/llm-agents/023-configure-a-planner.py"
    ```

- **`PlanReActPlanner`:** This planner instructs the model to follow a specific
  structure in its output: first create a plan, then execute actions (like
  calling tools), and provide reasoning for its steps. *It's particularly useful
  for models that don't have a built-in "thinking" feature*.

    ```python
    --8<-- "examples/inline/python/agents/llm-agents/024-configure-a-planner.py"
    ```

    The agent's response will follow a structured format:

    ```
    [user]: ai news
    [google_search_agent]: /*PLANNING*/
    1. Perform a Google search for "latest AI news" to get current updates and headlines related to artificial intelligence.
    2. Synthesize the information from the search results to provide a summary of recent AI news.

    /*ACTION*/
    /*REASONING*/
    The search results provide a comprehensive overview of recent AI news, covering various aspects like company developments, research breakthroughs, and applications. I have enough information to answer the user's request.

    /*FINAL_ANSWER*/
    Here's a summary of recent AI news:
    ....
    ```

Example for using built-in-planner:

```python
--8<-- "examples/inline/python/agents/llm-agents/025-configure-a-planner.py"
```

### Code execution

<div class="language-support-tag">
   <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

- **`code_executor` (Optional):** Provide a `BaseCodeExecutor` instance to allow
  the agent to execute code blocks found in the LLM's response. For more
  information, see [Code Execution with Gemini
  API](/integrations/code-execution/).

=== "Python"

    ```python
    --8<-- "examples/python/snippets/tools/built-in-tools/code_execution.py"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/CodeExecutionAgentApp.java:full_code"
    ```

## Code example

This following example demonstrates the core concepts discussed in this page.
More complex agents might incorporate schemas, context control, and planning.

??? "Code"
    Here's the complete basic `capital_agent`:

    === "Python"

        ```python
        --8<-- "examples/python/snippets/agents/llm-agent/capital_agent.py"
        ```

    === "TypeScript"

        ```typescript
        --8<-- "examples/typescript/snippets/agents/llm-agent/capital_agent.ts"
        ```

    === "Go"

        ```go
        --8<-- "examples/go/snippets/agents/llm-agents/main.go:full_code"
        ```

    === "Java"

        ```java
        --8<-- "examples/java/snippets/src/main/java/agents/LlmAgentExample.java:full_code"
        ```

    === "Kotlin"

        ```kotlin
        --8<-- "examples/kotlin/snippets/agents/llm-agent/CapitalAgent.kt:full_example"
        ```

## Additional features

ADK provides additional features for agents not covered in this guide, including
the following:

- **Callbacks:** Add more controls by intercepting agent execution points,
  including before and after model calls, and before and after tool calls with
  [Callbacks](/callbacks/types-of-callbacks/).
- **Graph-based workflows:** Compose LLM agents as steps in deterministic,
  graph-based pipelines using [Graph-based agent workflows](/graphs/). In Go
  v2.0.0, use `workflow.NewAgentNode` to wrap any LLM agent as a workflow node.
- **Multi-agent systems:** Advanced strategies for agent interaction, including
  agent transfer (`disallow_transfer_to_parent`, `disallow_transfer_to_peers`),
  and consistent identity and rules for every agent in your app (`GlobalInstructionPlugin`). See [Multi-agent
  workflows](/workflows/) and [collaborative agent
  teams](/workflows/collaboration/).
