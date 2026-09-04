# Evaluation for live agents

Supported in ADKPython v2.6.0

You can evaluate a live agent the way it actually gets used: a simulated user speaks its turns as audio, your agent answers over a real bidirectional session, and you score what it said back. The eval sets, criteria, and `adk eval` loop are the same ones you already use for text agents, covered in [Evaluate agents](https://adk.dev/evaluate/index.md).

## Drive the agent with speech

The `llm_audio` user simulator synthesizes each simulated user turn with a text-to-speech model and streams it to your agent as audio. That runs the path your users take end to end: speech in, voice activity detection, turn-taking, speech out, transcription. Feeding text to a voice agent skips all of it.

```json
{
  "user_simulator_config": {
    "type": "llm_audio",
    "model": "gemini-3.7-flash",
    "max_allowed_invocations": 10,
    "audio_model": "gemini-3.1-flash-tts-preview",
    "audio_model_configuration": {
      "response_modalities": ["AUDIO"],
      "speech_config": {
        "voice_config": {
          "prebuilt_voice_config": { "voice_name": "Kore" }
        },
        "language_code": "en-US"
      }
    }
  }
}
```

Two models do different jobs here. `model` decides what the simulated user says next, and `audio_model` turns that into speech. Changing `voice_name` and `language_code` is how you test the agent against different voices and accents, which is the kind of regression a text eval cannot catch.

Your eval cases stay as they are. The same conversation scenario or fixed conversation drives a text run or a voice run, so you can reuse a suite you already have. For the full schema, personas, and how to write scenarios, see [Audio user simulation](https://adk.dev/evaluate/user-sim/#audio-user-simulation-live-agents).

## Score with rubrics

A spoken reply is right in dozens of different phrasings, so criteria that compare against a reference string will fail correct answers. Rubric-based judges let you write the intent in natural language once and apply it across every conversation in the suite:

| Criterion                                                                                                                           | Scores                              |
| ----------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| [`rubric_based_final_response_quality_v1`](https://adk.dev/evaluate/criteria/#rubric_based_final_response_quality_v1)               | A single turn's reply               |
| [`rubric_based_tool_use_quality_v1`](https://adk.dev/evaluate/criteria/#rubric_based_tool_use_quality_v1)                           | Whether tools were called correctly |
| [`rubric_based_multi_turn_trajectory_quality_v1`](https://adk.dev/evaluate/criteria/#rubric_based_multi_turn_trajectory_quality_v1) | The conversation end to end         |

```json
{
  "criteria": {
    "rubric_based_multi_turn_trajectory_quality_v1": {
      "threshold": 0.7,
      "judge_model_options": { "judge_model": "gemini-3.7-flash" },
      "rubrics": [
        {
          "rubric_id": "verifies_identity_first",
          "rubric_content": {
            "text_property": "Across the call, the agent confirms the caller's name and validates their date of birth before disclosing any appointment details."
          }
        }
      ]
    }
  }
}
```

Reach for the trajectory criterion with [workflows](https://adk.dev/live/workflows/index.md), where what matters is that the agents ran in order and handed off cleanly rather than what any single turn said. Where the answer is genuinely fixed, [`tool_trajectory_avg_score`](https://adk.dev/evaluate/criteria/#tool_trajectory_avg_score) still checks the exact sequence of tool calls and ignores phrasing entirely.

## Run an eval

Add a `live_model_config` block to `test_config.json`. It is what puts the eval in live mode, and it is required for [Live models](https://adk.dev/live/models/#live-models), which are not served over the unary `generateContent` endpoint that text evals use:

```json
{
  "live_model_config": {
    "timeout_seconds": 300
  }
}
```

`timeout_seconds` (default 300) caps how long ADK waits for a turn to finish. Raise it if your agent narrates long tool calls, lower it to fail a stuck session faster.

```shell
adk eval path/to/your_agent \
  path/to/your_agent/live.evalset.json \
  --config_file_path path/to/your_agent/test_config.json
```

This needs the eval extras (`pip install "google-adk[eval]"`) and credentials for the Live API and the TTS model. The same run is available through `AgentEvaluator`, which is how you put voice evals in CI.

In `adk web`, the eval dialog has a **Standard | Live** toggle that exposes the input modality and the simulated user's voice and language. When the run finishes, ADK reassembles the audio into a transcript with a playable clip on every turn, so you can hear how the agent sounded instead of only reading what it said.

## Sample

The [`live_workflow` sample](https://github.com/google/adk-python/tree/main/contributing/samples/live/live_workflow) is a complete voice eval you can run: three live agents in a graph workflow, a tool call in the middle, and an eval set and `test_config.json` wired up with all three rubric criteria.
