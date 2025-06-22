# Conditional agents

## The `ConditionalAgent`

The `ConditionalAgent` is a [workflow agent](index.md) that routes execution between exactly two sub-agents based on a boolean predicate evaluated against the current `InvocationContext`.

Use the `ConditionalAgent` when you want to dynamically choose between two execution paths based on a specific condition.

### Example

* You want to build an agent that handles user requests differently based on intent. For instance, if the user wants to roll a die, it should route to a dice-rolling agent; if they want to check for prime numbers, it should route to a prime-checking agent. A `ConditionalAgent` can evaluate the user input and direct the flow accordingly.

As with other [workflow agents](index.md), the `ConditionalAgent` is not powered by an LLM, and is thus deterministic in how it executes based on the predicate result. That being said, workflow agents are concerned only with their execution (i.e., conditional routing), and not their internal logic; the tools or sub-agents of a workflow agent may or may not utilize LLMs.

### How it works

When the `ConditionalAgent`'s `Run Async` method is called, it performs the following actions:

1. **Condition Evaluation:** It evaluates the provided boolean predicate against the current `InvocationContext`. The predicate can be synchronous or asynchronous.
2. **Sub-Agent Selection:** If the predicate returns `True`, it executes the first sub-agent; if `False`, it executes the second sub-agent.

![Conditional Agent](../../assets/conditional-agent.png)

### Full Example: Intent-Based Routing

Consider a user request handler that routes based on intent:

* **Roll Agent:** An LLM Agent that handles dice rolling requests.
* **Prime Agent:** An LLM Agent that handles prime number checking requests.

A `ConditionalAgent` is perfect for this:

```py
ConditionalAgent(sub_agents=[RollAgent, PrimeAgent], condition=lambda ctx: 'roll' in ctx.user_content.lower())
```

This ensures the request is routed to the `RollAgent` if the user content contains 'roll', otherwise to the `PrimeAgent`. **The output from the chosen sub-agent is passed through as the result**.

???+ "Code"

    === "Python"
        ```py
        --8<-- "examples/python/snippets/agents/workflow-agents/conditional_agent_intent_routing.py:init"
        ```

    === "Java"
        ```java
        --8<-- "examples/java/snippets/src/main/java/agents/workflow/ConditionalAgentExample.java:init"
        ```
