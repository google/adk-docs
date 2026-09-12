# User simulation

Supported in ADKPython v1.18.0

When evaluating conversational agents, it is not always practical to use a fixed set of user prompts, as the conversation can proceed in unexpected ways. For example, if the agent needs the user to supply two values to perform a task, it may ask for those values one at a time or both at once. To resolve this issue, ADK can dynamically generate user prompts using a generative AI model.

To use this feature, you must specify a [`ConversationScenario`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/conversation_scenarios.py) which dictates the user's goals in their conversation with the agent. You may also specify a user persona that you expect the user to adhere to.

A `ConversationScenario` consists of the following components:

- `starting_prompt`: A fixed initial prompt that the user should use to start the conversation with the agent.
- `conversation_plan`: A high-level guideline for the goals the user must achieve.
- `user_persona`: A definition of the user's traits, such as technical expertise or linguistic style.

A sample conversation scenario for the [`hello_world`](https://github.com/google/adk-python/tree/main/contributing/samples/core/hello_world) agent is shown below:

```json
{
  "starting_prompt": "What can you do for me?",
  "conversation_plan": "Ask the agent to roll a 20-sided die. After you get the result, ask the agent to check if it is prime."
}
```

The LLM uses the `conversation_plan`, along with the conversation history, to dynamically generate user prompts.

You can also specify a pre-built `user_persona` in the following manner:

```json
{
  "starting_prompt": "What can you do for me?",
  "conversation_plan": "Ask the agent to roll a 20-sided die. After you get the result, ask the agent to check if it is prime.",
  "user_persona": "NOVICE"
}
```

While the conversation plan dictates what must be accomplished, the persona dictates how the model phrases its queries and reacts to the agent's responses.

## User personas

Supported in ADKPython v1.26.0

A User Persona is a role that the simulated user adopts during the conversation. It is defined by a set of **behaviors** that dictate how the user interacts with the agent, such as their communication style, how they provide information, and how they react to errors.

A `UserPersona` consists of the following fields:

- `id`: A unique identifier for the persona.
- `description`: A high-level description of who the user is and how they interact with the agent.
- `behaviors`: A list of `UserBehavior` objects that define specific traits.

Each `UserBehavior` includes:

- `name`: The name of the behavior.
- `description`: A summary of the expected behavior.
- `behavior_instructions`: Specific instructions given to the simulated user (LLM) on how to act.
- `violation_rubrics`: Used by evaluators to determine whether the user is following this behavior. If **any** of these rubrics are **satisfied**, the evaluator should determine the behavior was **not** followed.

## Pre-built Personas

ADK provides a set of pre-built personas composed of common behaviors. The table below summarizes the behaviors for each persona:

| Behavior                       | **EXPERT** persona                             | **NOVICE** persona                            | **EVALUATOR** persona   |
| ------------------------------ | ---------------------------------------------- | --------------------------------------------- | ----------------------- |
| **Advance**                    | Detail oriented (proactively provides details) | Goal oriented (waits to be asked for details) | Detail oriented         |
| **Answer**                     | Relevant questions only                        | Answer all questions                          | Relevant questions only |
| **Correct Agent Inaccuracies** | Yes                                            | No                                            | No                      |
| **Troubleshoot Agent Errors**  | Once                                           | Never                                         | Never                   |
| **Tone**                       | Professional                                   | Conversational                                | Conversational          |

## Example: Evaluate the [`hello_world`](https://github.com/google/adk-python/tree/main/contributing/samples/core/hello_world) agent with conversation scenarios

To add evaluation cases containing conversation scenarios to a new or existing [`EvalSet`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_set.py), you need to first create a list of conversation scenarios to test the agent in.

Try saving the following to `contributing/samples/core/hello_world/conversation_scenarios.json`:

```json
{
  "scenarios": [
    {
      "starting_prompt": "What can you do for me?",
      "conversation_plan": "Ask the agent to roll a 20-sided die. After you get the result, ask the agent to check if it is prime.",
      "user_persona": "NOVICE"
    },
    {
      "starting_prompt": "Hi, I'm running a tabletop RPG in which prime numbers are bad!",
      "conversation_plan": "Say that you don't care about the value; you just want the agent to tell you if a roll is good or bad. Once the agent agrees, ask it to roll a 6-sided die. Finally, ask the agent to do the same with 2 20-sided dice.",
      "user_persona": "EXPERT"
    }
  ]
}
```

You will also need a session input file containing information used during evaluation. Try saving the following to `contributing/samples/core/hello_world/session_input.json`:

```json
{
  "app_name": "hello_world",
  "user_id": "user"
}
```

Then, you can add the conversation scenarios to an `EvalSet`:

```bash
# (optional) create a new EvalSet
adk eval_set create \
  contributing/samples/core/hello_world \
  eval_set_with_scenarios

# add conversation scenarios to the EvalSet as new eval cases
adk eval_set add_eval_case \
  contributing/samples/core/hello_world \
  eval_set_with_scenarios \
  --scenarios_file contributing/samples/core/hello_world/conversation_scenarios.json \
  --session_input_file contributing/samples/core/hello_world/session_input.json
```

By default, ADK runs evaluations with metrics that require the agent's expected response to be specified. Since that is not the case for a dynamic conversation scenario, we will use an [`EvalConfig`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_config.py) with some alternate supported metrics.

Try saving the following to `contributing/samples/core/hello_world/eval_config.json`:

```json
{
  "criteria": {
    "hallucinations_v1": {
      "threshold": 0.5,
      "evaluate_intermediate_nl_responses": true
    },
    "safety_v1": {
      "threshold": 0.8
    }
  }
}
```

Finally, you can use the `adk eval` command to run the evaluation:

```bash
adk eval \
    contributing/samples/core/hello_world \
    --config_file_path contributing/samples/core/hello_world/eval_config.json \
    eval_set_with_scenarios \
    --print_detailed_results
```

## User simulator configuration

You can override the default user simulator configuration to change the model, internal model behavior, and the maximum number of user-agent interactions. The below `EvalConfig` shows the default user simulator configuration:

```json
{
  "criteria": {
    # same as before
  },
  "user_simulator_config": {
    "model": "gemini-flash-latest",
    "model_configuration": {
      "thinking_config": {
        "include_thoughts": true,
        "thinking_budget": 10240
      }
    },
    "max_allowed_invocations": 20,
    "include_function_calls": false
  }
}
```

- `model`: The model backing the user simulator.
- `model_configuration`: A [`GenerateContentConfig`](https://github.com/googleapis/python-genai/blob/6196b1b4251007e33661bb5d7dc27bafee3feefe/google/genai/types.py#L4295) which controls the model behavior.
- `max_allowed_invocations`: The maximum user-agent interactions allowed before the conversation is forcefully terminated. This should be set to be greater than the longest reasonable user-agent interaction in your `EvalSet`. The initial fixed prompt counts as an invocation. Setting this value to `-1` removes the innovation limit, which is not recommended.
- `include_function_calls`: Optional. Whether to include function calls and responses in the conversation history prompt given to the user simulator. Defaults to `false`.
- `custom_instructions`: Optional. Overrides the default instructions for the user simulator. The instruction string must contain the following formatting placeholders using [Jinja](https://jinja.palletsprojects.com/en/stable/templates/#) syntax (*do not substitute values in advance!*):
  - `{{ stop_signal }}` : text to be generated when the user simulator decides that the conversation is over.
  - `{{ conversation_plan }}` : the overall plan for the conversation that the user simulator must follow.
  - `{{ conversation_history }}` : the conversation between the user and the agent so far.
  - You can also access the `UserPersona` object through the `{{ persona }}` placeholder.

## Custom personas

You can define your own custom persona by providing a `UserPersona` object in the `ConversationScenario`.

Example of a custom persona definition:

```json
{
  "starting_prompt": "I need help with my account.",
  "conversation_plan": "Ask the agent to reset your password.",
  "user_persona": {
    "id": "IMPATIENT_USER",
    "description": "A user who is in a rush and gets easily frustrated.",
    "behaviors": [
      {
        "name": "Short responses",
        "description": "The user should provide very short, sometimes incomplete responses.",
        "behavior_instructions": [
            "Keep your responses under 10 words.",
            "Omit polite phrases."
        ],
        "violation_rubrics": [
            "The user response is over 10 words.",
            "The user response is overly polite."
        ]
      }
    ]
  }
}
```

## Generate evaluation cases via user simulation

Writing evaluation cases manually can be time-consuming and may not cover all potential failure modes. ADK provides a command to automatically generate diverse and realistic conversation scenarios based on your agent's definition using the Agent Platform Eval SDK.

Prerequisites: Agent Platform Credentials

Generating evaluation cases uses the [Vertex Gen AI Evaluation Service API](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/evaluation-overview). You must have a Google Cloud project with the Agent Platform API enabled and valid Application Default Credentials (ADC) configured in your environment.

### Command Syntax

```bash
adk eval_set generate_eval_cases \
    <AGENT_MODULE_FILE_PATH> \
    <EVAL_SET_ID> \
    --user_simulation_config_file=<PATH_TO_CONFIG_FILE>
```

### Configuration File Format

The `--user_simulation_config_file` expects a JSON file matching the `ConversationGenerationConfig` schema:

```json
{
  "count": 5,
  "generation_instruction": "Generate scenarios where the user asks to control home devices under different conditions.",
  "environment_context": "Available devices: device_1 (Light), device_2 (Thermostat).",
  "model_name": "gemini-flash-latest"
}
```

### Configuration Fields

- **`count`** (required): The number of conversation scenarios to generate.
- **`generation_instruction`** (optional): A natural language prompt guiding the specific types of scenarios or goals you want to test.
- **`environment_context`** (optional): Context describing the backend data or state accessible to the agent's tools. This helps the generator create queries that are grounded in realistic data (e.g., valid device IDs).
- **`model_name`** (required): The Gemini model used for generation (e.g., `gemini-flash-latest`).

## Audio user simulation for live agents

The user simulator is independent of whether the agent under test is a live (voice) agent, so the same `ConversationScenario` (or a fixed conversation) can drive both text and live evals. For live agents, the simulated user's turns can be synthesized to **audio** and streamed to the agent.

This is configured with the `llm_audio` user simulator in your eval config (`test_config.json`). It wraps the standard text simulator and converts each generated user turn to audio using a text-to-speech model. By default it uses Google Cloud Text-to-Speech (`cloud_tts`); a Gemini TTS model name may be used instead.

```json
{
  "criteria": {
    "tool_trajectory_avg_score": 1.0,
    "response_match_score": 0.5
  },
  "live_model_config": {
    "timeout_seconds": 300
  },
  "user_simulator_config": {
    "type": "llm_audio",
    "model": "gemini-2.5-flash",
    "audio_model": "cloud_tts",
    "audio_model_configuration": {
      "speech_config": {
        "voice_config": {
          "prebuilt_voice_config": { "voice_name": "en-US-Studio-O" }
        },
        "language_code": "en-US"
      }
    },
    "include_text_with_audio": true
  }
}
```

Key fields:

- `type`: `"llm_audio"` selects the audio user simulator.
- `audio_model`: `"cloud_tts"` for Google Cloud Text-to-Speech, or a Gemini TTS model name (e.g. `"gemini-2.5-flash-preview-tts"`).
- `audio_model_configuration.speech_config`: Selects the voice and language.
- `include_text_with_audio`: Whether the user turn also carries the text part alongside the generated audio.

Live models require live inference

Evaluating a live agent requires live (bidirectional streaming) inference, which is **not** the default. Enable it by adding a `live_model_config` block to your config file. Live API models (e.g. `gemini-*-live-*`) are not served over the unary `generateContent` endpoint that non-live eval uses, so running them without live mode fails.

`use_live` is an internal field set from `live_model_config`; putting it in a config file has no effect.

Using `cloud_tts` requires the `google-cloud-texttospeech` package (included in the `google-adk[eval]` extra) and access to the Cloud Text-to-Speech API.

See the sample at [`contributing/samples/live/live_non_blocking_tool_agent`](https://github.com/google/adk-python/tree/main/contributing/samples/live/live_non_blocking_tool_agent) for a complete, runnable live eval configuration.
