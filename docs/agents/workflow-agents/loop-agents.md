# Loop agents

## The `LoopAgent`

The `LoopAgent` is a workflow agent that executes its sub-agents in a loop (i.e. iteratively). It **_repeatedly runs_ a sequence of agents** for a specified number of iterations or until a termination condition is met.

Use the `LoopAgent` when your workflow involves repetition or iterative refinement, such as revising code.

### Example

* You want to build an agent that can generate images of food, but sometimes when you want to generate a specific number of items (e.g. 5 bananas), it generates a different number of those items in the image (e.g. an image of 7 bananas). You have two tools: `Generate Image`, `Count Food Items`. Because you want to keep generating images until it either correctly generates the specified number of items, or after a certain number of iterations, you should build your agent using a `LoopAgent`.

As with other [workflow agents](index.md), the `LoopAgent` is not powered by an LLM, and is thus deterministic in how it executes. That being said, workflow agents are only concerned only with their execution (i.e. in a loop), and not their internal logic; the tools or sub-agents of a workflow agent may or may not utilize LLMs.

### How it Works

When the `LoopAgent`'s `Run Async` method is called, it performs the following actions:

1. **Sub-Agent Execution:**  It iterates through the Sub Agents list _in order_. For _each_ sub-agent, it calls the agent's `Run Async` method.
2. **Termination Check:**

    _Crucially_, the `LoopAgent` itself does _not_ inherently decide when to stop looping. You _must_ implement a termination mechanism to prevent infinite loops.  Common strategies include:

    * **Max Iterations**: Set a maximum number of iterations in the `LoopAgent`. **The loop will terminate after that many iterations**.
    * **Escalation from sub-agent**: Design one or more sub-agents to evaluate a condition (e.g., "Is the document quality good enough?", "Has a consensus been reached?").  If the condition is met, the sub-agent can signal termination (e.g., by raising a custom event, setting a flag in a shared context, or returning a specific value).

![Loop Agent](../../assets/loop-agent.png)

### Full Example: Iterative Document Improvement

Imagine a scenario where you want to iteratively improve a document:

* **Writer Agent:** An `LlmAgent` that generates or refines a draft on a topic.
* **Critic Agent:** An `LlmAgent` that critiques the draft, identifying areas for improvement.

    ```py
    LoopAgent(sub_agents=[WriterAgent, CriticAgent], max_iterations=5)
    ```

In this setup, the `LoopAgent` would manage the iterative process.  The `CriticAgent` could be **designed to return a "STOP" signal when the document reaches a satisfactory quality level**, preventing further iterations. Alternatively, the `max iterations` parameter could be used to limit the process to a fixed number of cycles, or external logic could be implemented to make stop decisions. The **loop would run at most five times**, ensuring the iterative refinement doesn't continue indefinitely.

Using **`Idea -> Build -> Manage -> Grow`** as the "interface" or the sub-agents for a `LoopAgent` is the ideal way to model an autonomous, self-improving business or product.

You are essentially proposing to create a **Business Lifecycle Agent**, where the loop represents the continuous, iterative cycle of innovation and operation.

Let's break down exactly how this would work, using the `LoopAgent` framework you provided.

---

### The "Business Lifecycle" Loop Agent

Your main agent would be a `LoopAgent` configured to orchestrate the entire business process.

```python
BusinessLifecycleAgent = LoopAgent(
    sub_agents=[
        IdeaAgent,
        BuildAgent,
        ManageAgent,
        GrowAgent
    ],
    # The loop could run on a schedule (e.g., once per sprint/week)
    # or until a major business goal is met.
)
```

Now, let's define what each of the sub-agents would do.

#### 1. **`IdeaAgent` (The Innovator)**

*   **Type:** `LlmAgent`
*   **Purpose:** To generate the next set of improvements or actions.
*   **Inputs:**
    *   Analysis report from the `GrowAgent` (from the previous loop).
    *   New market data, user feedback, or bug reports.
    *   High-level business goals (e.g., "Increase user retention by 5%").
*   **Action:** Uses an LLM to brainstorm and define a clear, actionable plan.
*   **Output:** A structured "feature brief" or a "change request." For example: `{"action": "implement_gamification_badge", "priority": "high", "goal": "increase_engagement"}`.

#### 2. **`BuildAgent` (The Executor)**

*   **Type:** Workflow Agent (like our previous Kubernetes Agent).
*   **Purpose:** To take the plan from the `IdeaAgent` and make it a reality.
*   **Inputs:** The "feature brief" from the `IdeaAgent`.
*   **Action:** This agent does not use an LLM. It's a deterministic executor. It would:
    *   Translate the feature brief into technical steps.
    *   Interact with a CI/CD pipeline (e.g., GitHub Actions).
    *   Make calls to the Kubernetes API to deploy new code, update configurations, or provision resources for a client's "pod" (`helm upgrade`).
*   **Output:** A deployment confirmation: `{"status": "success", "version": "v2.1.4", "change": "implemented_gamification_badge"}`.

#### 3. **`ManageAgent` (The Operator)**

*   **Type:** Workflow Agent.
*   **Purpose:** To ensure the system is running smoothly after the change.
*   **Inputs:** The deployment confirmation from the `BuildAgent`.
*   **Action:**
    *   Monitors system health (Prometheus, Grafana).
    *   Checks resource usage of client pods.
    *   Gathers logs and performance metrics.
*   **Output:** A raw "Operational Status Report": `{"cpu_usage": "75%", "error_rate": "0.1%", "client_pod_health": "ok"}`.

#### 4. **`GrowAgent` (The Critic & Analyst)**

*   **Type:** `LlmAgent`
*   **Purpose:** To analyze the impact of the last loop's changes and decide if the cycle should continue. This is the **most important agent for controlling the loop.**
*   **Inputs:**
    *   The "Operational Status Report" from the `ManageAgent`.
    *   Business metrics (user analytics, revenue data, churn rates).
    *   The original "goal" from the `IdeaAgent`.
*   **Action:**
    *   Uses an LLM to analyze the data and answer the question: "Did the change we made in the `Build` phase achieve the `goal` set by the `Idea` phase?"
    *   Compares the outcome against the high-level business objectives.
*   **Output:** An "Analysis Report" and a **Termination Signal**.
    *   `{"analysis": "Gamification badge increased daily active users by 7%, exceeding the 5% goal.", "signal": "CONTINUE"}`
    *   `{"analysis": "The new feature caused a 15% increase in server costs with no significant engagement lift.", "signal": "PAUSE_FOR_REVIEW"}`

### How it Fits the `LoopAgent` Model Perfectly

This structure directly mirrors the "Iterative Document Improvement" example you provided:

*   `IdeaAgent` + `BuildAgent` = The "Writer Agent" (It creates/changes the product).
*   `ManageAgent` + `GrowAgent` = The "Critic Agent" (It evaluates the change).

The **`GrowAgent`** is the key to preventing infinite or wasteful loops. It can be designed to return a "STOP" or "PAUSE" signal when:
*   A major business objective has been met.
*   A change has had a negative impact and requires human intervention.
*   The cost of an iteration outweighs the potential benefits.

This turns your entire business operation into a self-correcting, goal-oriented, autonomous system. You've essentially designed a blueprint for an AI-driven CEO for your product.
???+ "Full Code"

    === "Python"
        ```py
        --8<-- "examples/python/snippets/agents/workflow-agents/loop_agent_doc_improv_agent.py:init"
        ```
    === "Java"
        ```java
        --8<-- "examples/java/snippets/src/main/java/agents/workflow/LoopAgentExample.java:init"
        ```

