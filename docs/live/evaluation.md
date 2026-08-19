# Evaluation

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v2.6.0</span>
</div>

You evaluate a live agent with the same tools you use for any ADK agent: eval sets, criteria,
and a simulated user. Live agents add one requirement and one option.

**Requirement: run evals in live mode.** Live API models are not served over the unary
`generateContent` endpoint that normal evals use, so an eval must open a bidirectional
streaming session. Enable it with `"use_live": true` in your `test_config.json`. Without it,
a live model fails at inference.

```json
{
  "criteria": {
    "tool_trajectory_avg_score": 1.0,
    "response_match_score": 0.5
  },
  "use_live": true
}
```

**Option: drive the agent with synthesized audio.** The simulated user's turns can be
converted to speech and streamed to the agent, exercising the audio path end to end. Set the
user simulator `type` to `llm_audio` and choose a voice. This is covered in full, with the
config schema and key fields, in
[Audio user simulation](../evaluate/user-sim.md#audio-user-simulation-live-agents).

Everything else — writing eval sets, choosing [criteria](../evaluate/criteria.md), and
[generating cases](../evaluate/user-sim.md#generate-evaluation-cases-via-user-simulation) —
works the same as for text agents. Start with [Evaluate agents](../evaluate/index.md).

For a complete, runnable live eval configuration, see the
[`live_non_blocking_tool_agent` sample](https://github.com/google/adk-python/tree/main/contributing/samples/live/live_non_blocking_tool_agent).
