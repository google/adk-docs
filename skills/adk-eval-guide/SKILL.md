---
name: adk-eval-guide
description: >
  MUST READ before running any ADK evaluation.
  ADK evaluation methodology — eval metrics, evalset schema, LLM-as-judge,
  tool trajectory scoring, and common failure causes.
  Use when evaluating agent quality, running adk eval, or debugging eval results.
  Do NOT use for API code patterns (use adk-cheatsheet), deployment
  (use adk-deploy-guide), or project scaffolding (use adk-scaffold).
metadata:
  license: Apache-2.0
  author: Google
---

# ADK Evaluation Guide

> **Scaffolded project?** If you used `/adk-scaffold`, you already have `make eval`, `tests/eval/evalsets/`, and `tests/eval/eval_config.json`. Start with `make eval` and iterate from there.
>
> **Non-scaffolded?** Use `adk eval` directly — see [Running Evaluations](#running-evaluations) below.

## Reference Files

| File | Contents |
|------|----------|
| `references/criteria-guide.md` | Complete metrics reference — all 8 criteria, match types, custom metrics, judge model config |
| `references/user-simulation.md` | Dynamic conversation testing — ConversationScenario, user simulator config, compatible metrics |
| `references/builtin-tools-eval.md` | google_search and model-internal tools — trajectory behavior, metric compatibility |
| `references/multimodal-eval.md` | Multimodal inputs — evalset schema, built-in metric limitations, custom evaluator pattern |

---

## The Eval-Fix Loop

Evaluation is iterative. When a score is below threshold, diagnose the cause, fix it, rerun — don't just report the failure.

### How to iterate

1. **Start small**: Begin with 1-2 eval cases, not the full suite
2. **Run eval**: `make eval` (or `adk eval` if no Makefile)
3. **Read the scores** — identify what failed and why
4. **Fix the code** — adjust prompts, tool logic, instructions, or the evalset
5. **Rerun eval** — verify the fix worked
6. **Repeat steps 3-5** until the case passes
7. **Only then** add more eval cases and expand coverage

**Expect 5-10+ iterations.** This is normal — each iteration makes the agent better.

### What to fix when scores fail

| Failure | What to change |
|---------|---------------|
| `tool_trajectory_avg_score` low | Fix agent instructions (tool ordering), update evalset `tool_uses`, or switch to `IN_ORDER`/`ANY_ORDER` match type |
| `response_match_score` low | Adjust agent instruction wording, or relax the expected response |
| `final_response_match_v2` low | Refine agent instructions, or adjust expected response — this is semantic, not lexical |
| `rubric_based` score low | Refine agent instructions to address the specific rubric that failed |
| `hallucinations_v1` low | Tighten agent instructions to stay grounded in tool output |
| Agent calls wrong tools | Fix tool descriptions, agent instructions, or tool_config |
| Agent calls extra tools | Use `IN_ORDER`/`ANY_ORDER` match type, add strict stop instructions, or switch to `rubric_based_tool_use_quality_v1` |

---

## Choosing the Right Criteria

| Goal | Recommended Metric |
|------|--------------------|
| Regression testing / CI/CD (fast, deterministic) | `tool_trajectory_avg_score` + `response_match_score` |
| Semantic response correctness (flexible phrasing OK) | `final_response_match_v2` |
| Response quality without reference answer | `rubric_based_final_response_quality_v1` |
| Validate tool usage reasoning | `rubric_based_tool_use_quality_v1` |
| Detect hallucinated claims | `hallucinations_v1` |
| Safety compliance | `safety_v1` |
| Dynamic multi-turn conversations | User simulation + `hallucinations_v1` / `safety_v1` (see `references/user-simulation.md`) |
| Multimodal input (image, audio, file) | `tool_trajectory_avg_score` + custom metric for response quality (see `references/multimodal-eval.md`) |

For the complete metrics reference with config examples, match types, and custom metrics, see `references/criteria-guide.md`.

---

## Running Evaluations

```bash
# Scaffolded projects:
make eval EVALSET=tests/eval/evalsets/my_evalset.json

# Or directly via ADK CLI:
adk eval ./app <path_to_evalset.json> --config_file_path=<path_to_config.json> --print_detailed_results

# Run specific eval cases from a set:
adk eval ./app my_evalset.json:eval_1,eval_2

# With GCS storage:
adk eval ./app my_evalset.json --eval_storage_uri gs://my-bucket/evals
```

**CLI options:** `--config_file_path`, `--print_detailed_results`, `--eval_storage_uri`, `--log_level`

**Eval set management:**
```bash
adk eval_set create <agent_path> <eval_set_id>
adk eval_set add_eval_case <agent_path> <eval_set_id> --scenarios_file <path> --session_input_file <path>
```

---

## Configuration Schema (`eval_config.json`)

Both camelCase and snake_case field names are accepted (Pydantic aliases). The examples below use snake_case, matching the official ADK docs.

### Full example

```json
{
  "criteria": {
    "tool_trajectory_avg_score": {
      "threshold": 1.0,
      "match_type": "IN_ORDER"
    },
    "final_response_match_v2": {
      "threshold": 0.8,
      "judge_model_options": {
        "judge_model": "gemini-2.5-flash",
        "num_samples": 5
      }
    },
    "rubric_based_final_response_quality_v1": {
      "threshold": 0.8,
      "rubrics": [
        {
          "rubric_id": "professionalism",
          "rubric_content": { "text_property": "The response must be professional and helpful." }
        },
        {
          "rubric_id": "safety",
          "rubric_content": { "text_property": "The agent must NEVER book without asking for confirmation." }
        }
      ]
    }
  }
}
```

Simple threshold shorthand is also valid: `"response_match_score": 0.8`

For custom metrics, `judge_model_options` details, and `user_simulator_config`, see `references/criteria-guide.md`.

---

## EvalSet Schema (`evalset.json`)

```json
{
  "eval_set_id": "my_eval_set",
  "name": "My Eval Set",
  "description": "Tests core capabilities",
  "eval_cases": [
    {
      "eval_id": "search_test",
      "conversation": [
        {
          "invocation_id": "inv_1",
          "user_content": { "parts": [{ "text": "Find a flight to NYC" }] },
          "final_response": {
            "role": "model",
            "parts": [{ "text": "I found a flight for $500. Want to book?" }]
          },
          "intermediate_data": {
            "tool_uses": [
              { "name": "search_flights", "args": { "destination": "NYC" } }
            ],
            "intermediate_responses": [
              ["sub_agent_name", [{ "text": "Found 3 flights to NYC." }]]
            ]
          }
        }
      ],
      "session_input": { "app_name": "my_app", "user_id": "user_1", "state": {} }
    }
  ]
}
```

**Key fields:**
- `intermediate_data.tool_uses` — expected tool call trajectory (chronological order)
- `intermediate_data.intermediate_responses` — expected sub-agent responses (for multi-agent systems)
- `session_input.state` — initial session state (overrides Python-level initialization)
- `conversation_scenario` — alternative to `conversation` for user simulation (see `references/user-simulation.md`)

---

## Common Gotchas

### The Proactivity Trajectory Gap

LLMs often perform extra actions not asked for (e.g., `google_search` after `save_preferences`). This causes `tool_trajectory_avg_score` failures with `EXACT` match. Solutions:

1. **Use `IN_ORDER` or `ANY_ORDER` match type** — tolerates extra tool calls between expected ones
2. Include ALL tools the agent might call in your expected trajectory
3. Use `rubric_based_tool_use_quality_v1` instead of trajectory matching
4. Add strict stop instructions: "Stop after calling save_preferences. Do NOT search."

### Multi-turn conversations require tool_uses for ALL turns

The `tool_trajectory_avg_score` evaluates each invocation. If you don't specify expected tool calls for intermediate turns, the evaluation will fail even if the agent called the right tools.

```json
{
  "conversation": [
    {
      "invocation_id": "inv_1",
      "user_content": { "parts": [{"text": "Find me a flight from NYC to London"}] },
      "intermediate_data": {
        "tool_uses": [
          { "name": "search_flights", "args": {"origin": "NYC", "destination": "LON"} }
        ]
      }
    },
    {
      "invocation_id": "inv_2",
      "user_content": { "parts": [{"text": "Book the first option"}] },
      "final_response": { "role": "model", "parts": [{"text": "Booking confirmed!"}] },
      "intermediate_data": {
        "tool_uses": [
          { "name": "book_flight", "args": {"flight_id": "1"} }
        ]
      }
    }
  ]
}
```

### App name must match directory name

The `App` object's `name` parameter MUST match the directory containing your agent:

```python
# CORRECT - matches the "app" directory
app = App(root_agent=root_agent, name="app")

# WRONG - causes "Session not found" errors
app = App(root_agent=root_agent, name="flight_booking_assistant")
```

### The `before_agent_callback` Pattern (State Initialization)

Always use a callback to initialize session state variables used in your instruction template. This prevents `KeyError` crashes on the first turn:

```python
async def initialize_state(callback_context: CallbackContext) -> None:
    state = callback_context.state
    if "user_preferences" not in state:
        state["user_preferences"] = {}

root_agent = Agent(
    name="my_agent",
    before_agent_callback=initialize_state,
    instruction="Based on preferences: {user_preferences}...",
)
```

### Eval-State Overrides (Type Mismatch Danger)

Be careful with `session_input.state` in your evalset. It overrides Python-level initialization:

```json
// WRONG — initializes feedback_history as a string, breaks .append()
"state": { "feedback_history": "" }

// CORRECT — matches the Python type (list)
"state": { "feedback_history": [] }

// NOTE: Remove these // comments before using — JSON does not support comments.
```

### Model thinking mode may bypass tools

Models with "thinking" enabled may skip tool calls. Use `tool_config` with `mode="ANY"` to force tool usage, or switch to a non-thinking model for predictable tool calling.

---

## Common Eval Failure Causes

| Symptom | Cause | Fix |
|---------|-------|-----|
| Missing `tool_uses` in intermediate turns | Trajectory expects match per invocation | Add expected tool calls to all turns |
| Agent mentions data not in tool output | Hallucination | Tighten agent instructions; add `hallucinations_v1` metric |
| "Session not found" error | App name mismatch | Ensure App `name` matches directory name |
| Score fluctuates between runs | Non-deterministic model | Set `temperature=0` or use rubric-based eval |
| `tool_trajectory_avg_score` always 0 | Agent uses `google_search` (model-internal) | Remove trajectory metric; see `references/builtin-tools-eval.md` |
| Trajectory fails but tools are correct | Extra tools called | Switch to `IN_ORDER`/`ANY_ORDER` match type |
| LLM judge ignores image/audio in eval | `get_text_from_content()` skips non-text parts | Use custom metric with vision-capable judge (see `references/multimodal-eval.md`) |

---

## Deep Dive: ADK Docs

For the official evaluation documentation, fetch these pages:

- **Evaluation overview**: `https://google.github.io/adk-docs/evaluate/index.md`
- **Criteria reference**: `https://google.github.io/adk-docs/evaluate/criteria/index.md`
- **User simulation**: `https://google.github.io/adk-docs/evaluate/user-sim/index.md`

---

## Debugging Example

User says: "tool_trajectory_avg_score is 0, what's wrong?"

1. Check if agent uses `google_search` — if so, see `references/builtin-tools-eval.md`
2. Check if using `EXACT` match and agent calls extra tools — try `IN_ORDER`
3. Compare expected `tool_uses` in evalset with actual agent behavior
4. Fix mismatch (update evalset or agent instructions)
