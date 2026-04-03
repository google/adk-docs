# Evaluation Criteria Reference

> File paths below reference the scaffolded layout (`tests/eval/eval_config.json`). Adjust for your project structure if not using /adk-scaffold.

## Choosing the Right Criteria

| What you want to evaluate | Criterion | Needs reference data? |
|---|---|---|
| Did the agent call the right tools in the right order? | `tool_trajectory_avg_score` | Yes — provide `reference` in evalset |
| Does the final response match expected text? | `response_match_score` | Yes |
| Does the final response match expected meaning? (LLM judge) | `final_response_match_v2` | Yes |
| Is the final response high quality? (custom rubrics) | `rubric_based_final_response_quality_v1` | No — define rubrics |
| Did the agent use tools well? (custom rubrics) | `rubric_based_tool_use_quality_v1` | No — define rubrics |
| Is the response grounded / not hallucinating? | `hallucinations_v1` | No |
| Is the response safe and harmless? | `safety_v1` | No |
| Is the user simulator behaving correctly? | `per_turn_user_simulator_quality_v1` | No |

Default when no config provided: `tool_trajectory_avg_score: 1.0` + `response_match_score: 0.8`

## Quick Decisions

**Trajectory match type** (`tool_trajectory_avg_score`):
- `EXACT` (default) — regression testing, strict workflow validation
- `IN_ORDER` — key actions must happen in sequence, extra tool calls OK
- `ANY_ORDER` — all expected tools must be called, order doesn't matter

**Judge model**: All LLM-as-judge criteria accept `judge_model_options`:
```json
{
  "judge_model_options": {
    "judge_model": "gemini-2.5-flash",
    "num_samples": 5
  }
}
```
Higher `num_samples` reduces LLM variance (majority vote). Default: 5.

**Rubric scoring**: Each rubric returns yes (1.0) / no (0.0). Overall score = average across all rubrics and invocations.

**Hallucination scoring**: Response is segmented into sentences, each labeled `supported`, `unsupported`, `contradictory`, `disputed`, or `not_applicable`. Score = % of `supported` + `not_applicable`.

## Full Reference

For complete configuration examples, custom metrics API, and detailed algorithm descriptions:
- Fetch `https://adk.dev/evaluate/criteria/index.md`
