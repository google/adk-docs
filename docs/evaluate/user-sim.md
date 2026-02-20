# User Simulation

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.18.0</span>
</div>

When evaluating conversational agents, it is not always practical to use a fixed
set of user prompts, as the conversation can proceed in unexpected ways.
For example, if the agent needs the user to supply two values to perform a task,
it may ask for those values one at a time or both at once.
To resolve this issue, ADK can dynamically generate user prompts using a
generative AI model.

To use this feature, you must specify a
[`ConversationScenario`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/conversation_scenarios.py)
which dictates the user's goals in their conversation with the agent.
A sample conversation scenario for the
[`hello_world`](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world)
agent is shown below:

```json
{
  "starting_prompt": "What can you do for me?",
  "conversation_plan": "Ask the agent to roll a 20-sided die. After you get the result, ask the agent to check if it is prime."
}
```

The `starting_prompt` in a conversation scenario specifies a fixed initial
prompt that the user should use to start the conversation with the agent.
Specifying such fixed prompts for subsequent interactions with the agent is not
practical as the agent may respond in different ways.
Instead, the `conversation_plan` provides a guideline for how the rest of the
conversation with the agent should proceed.
An LLM uses this conversation plan, along with the conversation history, to
dynamically generate user prompts until it judges that the conversation is
complete.

!!! tip "Try it in Colab"

    Test this entire workflow yourself in an interactive notebook on
    [Simulating User Conversations to Dynamically Evaluate ADK Agents](https://github.com/google/adk-samples/blob/main/python/notebooks/evaluation/user_simulation_in_adk_evals.ipynb).
    You'll define a conversation scenario, run a "dry run" to check the
    dialogue, and then perform a full evaluation to score the agent's responses.

## Example: Evaluating the [`hello_world`](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world) agent with conversation scenarios

To add evaluation cases containing conversation scenarios to a new or existing
[`EvalSet`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_set.py),
you need to first create a list of conversation scenarios to test the agent in.

Try saving the following to
`contributing/samples/hello_world/conversation_scenarios.json`:

```json
{
  "scenarios": [
    {
      "starting_prompt": "What can you do for me?",
      "conversation_plan": "Ask the agent to roll a 20-sided die. After you get the result, ask the agent to check if it is prime."
    },
    {
      "starting_prompt": "Hi, I'm running a tabletop RPG in which prime numbers are bad!",
      "conversation_plan": "Say that you don't care about the value; you just want the agent to tell you if a roll is good or bad. Once the agent agrees, ask it to roll a 6-sided die. Finally, ask the agent to do the same with 2 20-sided dice."
    }
  ]
}
```

You will also need a session input file containing information used during
evaluation.
Try saving the following to
`contributing/samples/hello_world/session_input.json`:

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
  contributing/samples/hello_world \
  eval_set_with_scenarios

# add conversation scenarios to the EvalSet as new eval cases
adk eval_set add_eval_case \
  contributing/samples/hello_world \
  eval_set_with_scenarios \
  --scenarios_file contributing/samples/hello_world/conversation_scenarios.json \
  --session_input_file contributing/samples/hello_world/session_input.json
```

By default, ADK runs evaluations with metrics that require the agent's expected
response to be specified.
Since that is not the case for a dynamic conversation scenario, we will use an
[`EvalConfig`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_config.py)
with some alternate supported metrics.

Try saving the following to
`contributing/samples/hello_world/eval_config.json`:

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
    contributing/samples/hello_world \
    --config_file_path contributing/samples/hello_world/eval_config.json \
    eval_set_with_scenarios \
    --print_detailed_results
```

## User simulator configuration

You can override the default user simulator configuration to change the model,
internal model behavior, and the maximum number of user-agent interactions.
The below `EvalConfig` shows the default user simulator configuration:

```json
{
  "criteria": {
    # same as before
  },
  "user_simulator_config": {
    "model": "gemini-2.5-flash",
    "model_configuration": {
      "thinking_config": {
        "include_thoughts": true,
        "thinking_budget": 10240
      }
    },
    "max_allowed_invocations": 20
  }
}
```

* `model`: The model backing the user simulator.
* `model_configuration`: A
[`GenerateContentConfig`](https://github.com/googleapis/python-genai/blob/6196b1b4251007e33661bb5d7dc27bafee3feefe/google/genai/types.py#L4295)
which controls the model behavior.
* `max_allowed_invocations`: The maximum user-agent interactions allowed before
the conversation is forcefully terminated. This should be set to be greater than
the longest reasonable user-agent interaction in your `EvalSet`.
* `custom_instructions`: Optional. Overrides the default instructions for the
user simulator. The instruction string must contain the following formatting
placeholders exactly as shown below (*do not substitute values in advance!*):
    * `{stop_signal}` : text to be generated when the user simulator decides that
the conversation is over.
    * `{conversation_plan}` : the overall plan for the conversation that the user
simulator must follow.
    * `{conversation_history}` : the conversation between the user and the agent
so far.
