---
catalog_title: Model Consult
catalog_description: Escalate hard reasoning from fast executors to stronger advisor models
catalog_icon: /integrations/assets/adk.png
catalog_tags: ["resilience", "observability", "google"]
---

# Model Consult tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v2.11.0</span>
</div>

Agents that use a single model face a tradeoff. A fast, low-cost model keeps routine steps quick and less resource intensive, but may be less well suited for thorough analysis and decisions on complex tasks. In contrast, a stronger model handles complex decisions well but increases the response time and resource costs for each agent step.

Model Consult lets an agent use the benefits of both. The agent runs on a fast executor model, and when it reaches a decision it cannot resolve confidently, it calls the Model Consult tool to get guidance from a stronger advisor model. The agent then continues the task itself, using its own tools. The agent uses the stronger model only for the steps that need it, and if a consultation fails or the consultation budget is spent, the agent keeps working with the information it already has.

## Use cases

- **Cost optimization**: Run an agent's routine orchestration and tool loops on a lower-cost model, and have the agent consult a stronger model only for the steps that need it.
- **Policy reconciliation**: Let an agent escalate complex, multi-clause policy decisions to a frontier model, then act on the guidance with its own tools.
- **Loop rescue**: Help an agent break out of a repetitive loop by having it consult a stronger model when it emits the same tool call repeatedly.

## Prerequisites

- ADK Python v2.11.0 or later.
- Access to two models: a lower-cost executor model and a stronger advisor model, such as Gemini Flash and Gemini Pro hosted on Google Cloud.
- Model credentials configured for ADK: either a Google Cloud project with the Vertex AI API enabled, or a Gemini API key.

## Installation

Model Consult is a native tool included directly in the ADK Python package.

```bash
pip install "google-adk>=2.11.0"
```

## Use with agent

Attach `ModelConsultTool` to an `Agent` alongside your domain tools, such as the example `lookup_order` function below. The tool registers the `model_consult` function declaration and appends a default escalation policy to the executor's system instruction, giving the agent clear rules on when and how to consult the advisor.

```python
from google.adk.agents import Agent
from google.adk.tools import ModelConsultTool

def lookup_order(order_id: str) -> dict[str, str]:
    """Looks up order status by identifier."""
    return {"order_id": order_id, "status": "held_for_fraud_review"}

root_agent = Agent(
    model="gemini-flash-latest",
    name="support_executor",
    instruction=(
        "You are an order support assistant. Resolve customer issues using"
        " your tools."
    ),
    tools=[
        lookup_order,
        ModelConsultTool(
            model="gemini-pro-latest",  # Advisor model
            max_uses=2,
            session_max_uses=5,
            thinking_level="high",
        ),
    ],
)
```

In this example:

- The `support_executor` agent runs on a fast model (`gemini-flash-latest`) and attempts to resolve the user's issue using its `lookup_order` tool.
- The executor model determines when to call `model_consult`. In default setup, the executors are instructed to call `model_consult` before committing to a decision, when stuck, and before declaring a task done.
- `ModelConsultTool` intercepts the call, verifies the max_uses budget, and packages the current session events along with the `lookup_order` tool's description into a single advisor consultation.
- The advisor model evaluates the context and returns structured text guidance, allowing the `support_executor` to resume control, execute any recommended tools, and finish the turn.

## Available tools

| Tool            | Description                                                                                                   |
| --------------- | ------------------------------------------------------------------------------------------------------------- |
| `model_consult` | Escalates the session history and a specific question to a stronger advisor model to get structured guidance. |

## How it works

When the executor calls `model_consult`, `ModelConsultTool` performs four steps and returns a structured dictionary to the executor:

1. **Budget verification** — `ModelConsultTool` checks the per-turn counter against `max_uses` and the session-wide counter against `session_max_uses`. If either cap has been reached, the tool returns `"status": "limit_reached"` immediately without calling the advisor model, and instructs the executor to proceed with the information already gathered.
2. **Context handover** — `ModelConsultTool` packages the consultation into a single `role='user'` `types.Content` message. When `include_agent_instruction` and `include_tool_inventory` are `True`, the message begins with the resolved executor instruction and sibling tool inventory. Next, `ModelConsultTool` converts the non-partial, non-rewound events in `Session.events` according to `ModelConsultContextConfig`, labeling text parts by speaker and flattening prior tool calls and tool responses into readable text summaries while excluding any in-flight `model_consult` call. Finally, `ModelConsultTool` appends a handoff part containing the active agent name, the executor's question, and any extra `context` string passed by the executor.
3. **Tool-less advisor call** — `ModelConsultTool` calls the configured advisor `BaseLlm` with tool calling disabled and the default advisor system instruction, or a custom `advisor_instruction` when provided. Because tool declarations are excluded from the advisor request, the advisor cannot execute tools or produce side effects on its own; it can only return text guidance naming which tools the executor should invoke next and with what arguments.
4. **Structured tool response** — `ModelConsultTool` never raises an exception back into the agent loop. Instead, it returns a dictionary with a `status` value, as described in [Response status values](#response-status-values).

### Inspecting tool calls

By default, `adk run` in human-readable mode only prints final text responses (`[support_executor]: ...`) and hides intermediate tool calls. Users can inspect `model_consult` calls and verify the advisor's response in three ways:

1. **ADK Web UI** — from a clone of [`adk-python`](https://github.com/google/adk-python), run `adk web contributing/samples/tools`:
   In the chat pane, each consultation appears as a `model_consult` tool event. Click the `model_consult` event to open the **Events / Trace** inspector on the left:
   - **`functionCall`** shows the exact `question` (and optional `context`) the executor sent to the advisor.
   - **`functionResponse`** shows the structured dictionary returned by `ModelConsultTool`, including `"status"`, `"guidance"`, `"advisor_model"`, `"thinking_level"`, `"consults"`, `"usage"`, and `"latency_ms"`.

2. **ADK CLI**:
   Use the `adk run` command to output every session event—including the `functionCall` and `functionResponse` for `model_consult`—as JSON. Choose your mode:
   - **Single-query mode:** Pass `--jsonl` to stream the events as JSON lines to stdout:
     ```bash
     adk run contributing/samples/tools/model_consult \
       "Customer CUST-108 wants a full refund to their original payment method for order ORD-502." \
       --jsonl
     ```
   - **Interactive mode:** Pass `--save_session` to save the full session log on exit:
     ```bash
     adk run contributing/samples/tools/model_consult --save_session --session_id consult_demo
     ```

3. **Programmatically via `Runner.run_async` events**:
   When running the agent in Python, inspect `event.get_function_calls()` and `event.get_function_responses()` for `name == "model_consult"`:

   ```python
   async for event in runner.run_async(user_id="u1", session_id="s1", new_message=msg):
       for resp in event.get_function_responses():
           if resp.name == "model_consult":
               print(resp.response["status"], resp.response.get("guidance"))
               print("Consult budget:", resp.response.get("consults"))
               print("Advisor token usage:", resp.response.get("usage"))
   ```

### Response status values

The `status` field of the dictionary that `model_consult` returns has one of the following values:

| Status            | Returned when                                                                           | Fields                                                                           | Consultation budget                           |
| ----------------- | --------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | --------------------------------------------- |
| `ok`              | The advisor returns guidance.                                                           | `guidance`, `advisor_model`, `thinking_level`, `consults`, `usage`, `latency_ms` | Increments the per-turn and session counters. |
| `limit_reached`   | `max_uses` or `session_max_uses` is already exhausted. The advisor model is not called. | `message`, `consults`                                                            | Not consumed.                                 |
| `error`           | The advisor call times out, fails, or produces no visible text.                         | `error`, `message`, `advisor_model`, `consults`                                  | Not consumed.                                 |
| `invalid_request` | `question` is empty or whitespace-only.                                                 | `message`                                                                        | Not consumed.                                 |

A successful consultation returns the following dictionary structure. The token counts and latency shown are illustrative, not representative measurements:

```json
{
    "status": "ok",
    "guidance": "1. Call lookup_order with order_id='ORD-42'.",
    "advisor_model": "gemini-3.1-pro-preview",
    "thinking_level": "high",
    "consults": {
        "used_this_turn": 1,
        "max_uses": 2,
        "used_this_session": 1,
        "session_max_uses": 5,
        "remaining": 1
    },
    "usage": {
        "prompt_tokens": 612,
        "output_tokens": 184,
        "thoughts_tokens": 320,
        "total_tokens": 1116
    },
    "latency_ms": 842.5
}
```

## Best practices

Model Consult works without extra configuration. Use these practices to improve results:

- Enable thinking on the executor model.
- Keep the default escalation policy, or steer the escalation policy in executor prompts for your use cases.

### Enable thinking on the executor

The executor decides when to call `model_consult`, so it makes better decisions when it can reason. Enable thinking on the executor model. For example, use a lighter model with dynamic thinking.

### Customize when the executor consults the advisor

An `ModelConsultTool` object adds an escalation policy to the executor's system instruction. By default, the policy tells the executor to call `model_consult` before it commits to a decision, when it is stuck, and before it declares a task done. These cover the planning, diagnosing, and reviewing triggers in the following table.

To replace the default policy, pass your own text in `executor_instruction`. To remove the policy, pass an empty string (`""`).

```python
ModelConsultTool(
    executor_instruction=(
        "Call model_consult before your first response, and whenever a"
        " tool call fails for a reason you cannot explain."
    ),
)
```

### Common consultation triggers

The following table lists common reasons to consult the advisor, with triggers that you can add to `executor_instruction`.

| Reason   | Why it helps                                                                                            | Example triggers                                                                                                                                                                                                                                                                                                   |
| --- | --- | --- |
| Plan     | A wrong interpretation or approach early in a task affects every later step and wastes time and tokens. | - Before the first response.<br>- After the executor gathers facts and before it starts the main work.<br>- When the request proposes a solution, to ask how to verify it.<br>- When several approaches or interpretations are possible and no evidence favors one.<br>- For request types that you know are difficult. |
| Diagnose | A failure or contradiction means that one of the executor's assumptions is wrong.                       | - A tool call fails or returns an unexpected result, and the executor cannot explain why.<br>- The executor repeats the same tool call, or a close variation, without new information.<br>- The executor reverses its own work.<br>- Two sources or tool results disagree.<br>- The executor concludes that the request is wrong. |
| Review   | Checking the result against the requirements finds errors and gaps before the user does.                | - Before the final answer.<br>- After the executor completes a substantial part of a complex task. |

## Configuration options

The `ModelConsultTool` object configures advisor model selection, consultation budgets, and prompt overrides, while `ModelConsultContextConfig` controls how session events are formatted and bounded before handover.

### ModelConsultTool options

The `ModelConsultTool` class accepts the following constructor arguments:

| Option                      | Type                          | Default               | Description                                                                                                                                      |
| --------------------------- | ----------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `model`                     | `str` \| `BaseLlm`             | `'gemini-3.1-pro-preview'`                                                                                                                       | Advisor model name resolved through ADK's model registry, or a pre-configured `BaseLlm` instance. The default is a preview model and is subject to change. |
| `max_uses`                  | `int`                         | `None`                | Maximum successful consultations per user turn. `None` means no per-turn cap.                                                                    |
| `session_max_uses`          | `int`                         | `None`                | Maximum successful consultations across the entire session. `None` means no session-wide cap.                                                    |
| `thinking_level`            | `str` \| `types.ThinkingLevel` | `'high'`                                                                                                                                         | Reasoning effort for the advisor model: `'minimal'`, `'low'`, `'medium'`, `'high'`, a `types.ThinkingLevel` enum value, or `'off'`, `'none'`, or `None` to leave thinking unset. |
| `max_output_tokens`         | `int`                         | `None`                | Optional cap on advisor output tokens, covering both visible output and thinking tokens on reasoning models.                                     |
| `timeout_seconds`           | `float`                       | `None`                | Per-call wall-clock timeout in seconds. `None` means no tool-level timeout.                                                                      |
| `context_config`            | `ModelConsultContextConfig`   | `None`                | Controls how session history is packaged and bounded for the advisor.                                                                            |
| `executor_instruction`      | `str`                         | `None`                | Overrides the default escalation policy automatically appended to the executor's `system_instruction`. Pass `""` to disable automatic injection. |
| `advisor_instruction`       | `str`                         | `None`                | Overrides the default system instruction sent to the advisor model.                                                                              |
| `description`               | `str`                         | `None`                | Overrides the default tool description shown to the executor model.                                                                              |
| `include_agent_instruction` | `bool`                        | `True`                | Forwards the executor agent's own instruction to the advisor so guidance respects the executor's constraints.                                    |
| `include_tool_inventory`    | `bool`                        | `True`                | Includes the names and descriptions of the executor's other tools in the advisor consultation prompt.                                            |
| `generate_content_config`   | `types.GenerateContentConfig` | `None`                | Base generation config cloned per advisor call, such as `temperature` or `safety_settings`.                                                      |
| `name`                      | `str`                         | `'model_consult'`     | Tool name exposed to the executor model.                                                                                                         |

### ModelConsultContextConfig options

`ModelConsultContextConfig` controls how `Session.events` is converted into the advisor's input contents:

| Option             | Type   | Default  | Description                                                                                                                                                                                                |
| ------------------ | ------ | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `include_session`  | `bool` | `True`   | Sends the converted `Session.events` history when `True`, or omits prior session events when `False`.                                                                                                      |
| `max_events`       | `int`  | `None`   | Keeps at most this many of the most recent non-partial session events before character budgeting. `None` keeps all events.                                                                                 |
| `max_chars`        | `int`  | `200000` | Character budget across all handed-over session turns. `None` disables the character budget.                                                                                                               |
| `max_part_chars`   | `int`  | `4000`   | Per-part character cap on rendered tool calls, tool results, and code blocks, with plain text parts allowed eight times this cap.                                                                          |
| `include_media`    | `bool` | `True`   | Forwards inline media and file references to the advisor model when `True`, or replaces them with text placeholders when `False`. Set to `False` if session media should not be sent to the advisor model. |
| `include_thoughts` | `bool` | `False`  | Includes the executor's internal thought parts in the advisor handover when `True`.                                                                                                                        |

## Additional resources

- [Model Consult Unit Guide](https://github.com/google/adk-python/blob/main/docs/guides/tools/model_consult/model_consult_tool/index.md)
