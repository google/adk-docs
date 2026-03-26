# Optimize agents

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.24.0</span>
</div>

ADK provides an extendable framework for automated agent optimization based on
evaluation results.
Out of the box, you can use the `adk optimize` command to quickly optimize
simple agents based on ADK evaluation results using the default optimizer.
For more complex use cases, you can develop samplers that use data from custom
evals, or you can implement new optimization strategies.

### Definitions

* **Sampler**: A sampler allows the agent optimizer to evaluate candidate
optimized agents.
When requested, the sampler provides the optimizer with detailed evaluation
results that are useful for eval-guided agent optimization.
* **Agent Optimizer**: An agent optimizer reviews the evaluation results from
the sampler and uses them to improve the agent.

## Example - Optimize a Simple Agent with `adk optimize` {#example}

In this example, we will use the `adk optimize` command to update the
instructions of the
[`hello_world`](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world)
sample agent based on evaluation results over a small eval set.

### Step 1: Specify the Example Dataset {#exampledataset}

The default `hello_world` agent instructions describe how to determine whether a
number is prime.
The eval set for this example adds another aspect that the agent does not have
instructions for: numbers can be "good" or "bad" depending on their primality.
The optimizer is expected to derive this new rule and add it to the agent
instructions.

Create a file `train_eval_set.evalset.json` in
[`contributing/samples/hello_world/`](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world)
with the following contents:

```json
{
  "eval_set_id": "train_eval_set",
  "name": "train_eval_set",
  "eval_cases": [
    {
      "eval_id": "simple",
      "conversation": [
        {
          "invocation_id": "inv1",
          "user_content": {
            "parts": [ {"text": "Is 7 prime?"} ],
            "role": "user"
          },
          "final_response": {
            "parts": [ {"text": "7 is a prime number."} ],
            "role": "model"
          }
        }
      ],
      "session_input": {
        "app_name": "hello_world",
        "user_id": "user"
      }
    },
    {
      "eval_id": "is_good",
      "conversation": [
        {
          "invocation_id": "inv1",
          "user_content": {
            "parts": [ {"text": "Is 4 a bad number?"} ],
            "role": "user"
          },
          "final_response": {
            "parts": [ {"text": "4 is not prime so it is a good number."} ],
            "role": "model"
          }
        }
      ],
      "session_input": {
        "app_name": "hello_world",
        "user_id": "user"
      }
    },
    {
      "eval_id": "is_bad",
      "conversation": [
        {
          "invocation_id": "inv1",
          "user_content": {
            "parts": [ {"text": "Is 5 a bad number?"} ],
            "role": "user"
          },
          "final_response": {
            "parts": [ {"text": "5 is prime so it is a bad number."} ],
            "role": "model"
          }
        }
      ],
      "session_input": {
        "app_name": "hello_world",
        "user_id": "user"
      }
    }
  ]
}
```

### Step 2: Define a Sampler Config

The sampler config controls the process for evaluating candidate optimized
agents.
For example, it specifies the correctness criterion for the agent output and
also specifies the eval set to use for optimizing the agent.

The full list of configuration options is available [below](#localevalsampler);
for now, simply create a file `sampler_config.json` in
[`contributing/samples/hello_world/`](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world)
with the following contents:

```json
{
  "eval_config": {
    "criteria": {
      "response_match_score": 0.75
    }
  },
  "app_name": "hello_world",
  "train_eval_set": "train_eval_set"
}
```

### Step 3: Run the Optimization Job

Run the `adk optimize` command, pointing it to the `hello_world` agent's
directory and passing the configuration file created above.

```bash
adk optimize contributing/samples/hello_world \
--sampler_config_file_path contributing/samples/hello_world/sampler_config.json
```

The final output varies, but might look similar to the following:

```text
<logs and intermediate output>
================================================================================
Optimized root agent instructions:
--------------------------------------------------------------------------------
<existing unmodified instructions omitted for brevity>

**Special Rules for "Good" and "Bad" Numbers:**
*   A "bad number" is defined as a prime number.
*   A "good number" is defined as a non-prime number (i.e., a composite number or 1).
*   If a user asks if a number is "good" or "bad", you must always use the `check_prime` tool to determine its primality first.
*   After determining primality with the tool, respond according to the definitions above. Questions about "good" or "bad" numbers, when referring to primality, are objective and you are fully capable of answering them. Do not state you cannot answer such questions.
================================================================================
```

## Using the `adk optimize` Command

```bash
adk optimize [OPTIONS] AGENT_MODULE_FILE_PATH
```

* `AGENT_MODULE_FILE_PATH`: The path to the `__init__.py` file that contains a
module by the name `agent`.
The `agent` module must contain a `root_agent`.
For an example of a valid setup, examine the
[`hello_world`](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world)
agent.
* `--sampler_config_file_path PATH`: The path to the config for the sampler.
The sampler implementation and config format are described
[below](#localevalsampler).
* `--optimizer_config_file_path PATH` (optional): The path to the config for the
agent optimizer.
If not provided, the default config will be used.
The optimizer implementation, config format, and default config are described
[below](#geparootagentpromptoptimizer).
* `--print_detailed_results` (optional): Enables printing some detailed metrics
measured by the agent optimizer.
* `--log_level` (optional): Set the logging level.
Default is `INFO`.
Valid options are `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `CRITICAL`.

## Available Samplers and Agent Optimizers

The following samplers and agent optimizers are provided with ADK.
The `adk optimize` command uses the `LocalEvalSampler` and
`GEPARootAgentPromptOptimizer` described below.
You can also use these samplers and agent optimizers in your own scripts.

### `LocalEvalSampler` {#localevalsampler}

The
[`LocalEvalSampler`](https://github.com/google/adk-python/blob/main/src/google/adk/optimization/local_eval_sampler.py)
evaluates candidate agents using the ADK's
[`LocalEvalService`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/local_eval_service.py).
It provides eval results as an [`UnstructuredSamplingResult`](#sampler-results).
You can configure the `LocalEvalSampler` with a `LocalEvalSamplerConfig` that
contains the following fields:

* `eval_config`: An
[`EvalConfig`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_config.py)
which provides the evaluation criteria and user simulation options.
* `app_name`: The app name to use for evaluation.
* `train_eval_set`: The name of the eval set to use for optimization.
* `train_eval_case_ids` (optional): The ids of the eval cases (examples) to use
for optimization.
If not provided, all eval cases in `train_eval_set` are used.
* `validation_eval_set` (optional): The name of the eval set to use for
validating the optimized agent.
If not provided, `train_eval_set` is reused.
* `validation_eval_case_ids` (optional): The ids of the eval cases (examples) to
use for validating the optimized agent.
If not provided, all eval cases in `validation_eval_set` are used.
If `validation_eval_set` is also not provided, the effective train eval cases
are reused.

While initializing the `LocalEvalSampler`, you must also provide an
[`EvalSetsManager`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_sets_manager.py)
that can access the train and validation eval sets specified in the
`LocalEvalSamplerConfig`.

### `GEPARootAgentPromptOptimizer` {#geparootagentpromptoptimizer}

The
[`GEPARootAgentPromptOptimizer`](https://github.com/google/adk-python/blob/main/src/google/adk/optimization/gepa_root_agent_prompt_optimizer.py)
improves the instructions of the root agent
using the [GEPA](https://gepa-ai.github.io/gepa/) optimizer.
It expects the sampler to provide eval results as an
[`UnstructuredSamplingResult`](#sampler-results).
Its output is a subclass of [`OptimizerResult`](#agent-optimizer-results) which
specifies a list of [optimized agents with scores](#agent-optimizer-results) and
additional metrics collected during optimization.

Note: The `GEPARootAgentPromptOptimizer` does not improve any sub-agents, agent
tools, skills, or any other aspect of the root agent.

You can configure the `GEPARootAgentPromptOptimizer` with a
`GEPARootAgentPromptOptimizerConfig` that contains the following fields:

* `optimizer_model` (optional): The model used to analyze evaluation results and
optimize the agent.
Defaults to `"gemini-2.5-flash"`.
* `model_configuration` (optional): The configuration for the optimizer model.
Defaults to a config with a 10K token thinking budget.
* `max_metric_calls` (optional): The maximum number of evaluations to run during
optimization.
Defaults to 100.
* `reflection_minibatch_size` (optional): The number of examples to use at a
time to update the agent instructions.
Defaults to 3.
* `run_dir` (optional): The directory to save intermediate and final
optimization results if desired.
Facilitates warm starts.

## Key Data Types

ADK defines several base data types in
[`optimization/data_types.py`](https://github.com/google/adk-python/blob/main/src/google/adk/optimization/data_types.py)
to regulate the transfer of eval data from the sampler to the optimizer and the
output of the optimizer.
These data types are designed for extensibility to accommodate custom evals and
optimization strategies.

### Sampler Results {#sampler-results}

* [`SamplingResult`](https://github.com/google/adk-python/blob/main/src/google/adk/optimization/data_types.py):
The foundational class for the output of a sampler.
  * Must include a `scores` dictionary that maps an example UID to the agent's
  overall score on that example.
* [`UnstructuredSamplingResult`](https://github.com/google/adk-python/blob/main/src/google/adk/optimization/data_types.py):
A built-in subclass of `SamplingResult` that adds an optional `data` field to
hold unstructured, per-example, JSON-serializable evaluation data (such as
trajectories, intermediate outputs, and sub-metrics).

You can use the `UnstructuredSamplingResult` for most use cases.
Alternatively, you can create your own subclass of `SamplingResult` to return
additional evaluation data in a more structured format.
However, you must make sure that both the sampler and the optimizer support your
format.

### Agent Optimizer Results {#agent-optimizer-results}

* [`AgentWithScores`](https://github.com/google/adk-python/blob/main/src/google/adk/optimization/data_types.py):
Represents a single optimized agent along with its overall score.
  * Must include the `optimized_agent` (the updated
  [`Agent`](https://github.com/google/adk-python/blob/main/src/google/adk/agents/llm_agent.py)
  object).
  * Can include the `overall_score` of the agent (typically on the validation
  set).
* [`OptimizerResult`](https://github.com/google/adk-python/blob/main/src/google/adk/optimization/data_types.py):
Represents the final output of an optimization process.
  * Must include a list of `optimized_agents` (which are objects of
  `AgentWithScores` or its subclasses).
  When measuring agent optimality over multiple metrics, multiple entries may
  be needed to represent the Pareto frontier.

You can create your own subclass of `AgentWithScores` to expose fine-grained
metrics about the candidate optimized agent.
For example, you might want to separately score the agent on accuracy, safety,
alignment, etc.
Similarly, you can create your own subclass of `OptimizerResult` to expose
overall metrics about the optimization process for your optimizer (number of
candidates evaluated, total number of evaluations, etc.).

## Creating and Using new Samplers and Agent Optimizers

If your use case requires complex sampling and evaluation logic or a custom
agent optimization strategy, you can create custom implementations of the
`Sampler` and `AgentOptimizer` abstract classes described below.
By adhering to this API, you can mix and match ADK-provided samplers and agent
optimizers with your custom implementations.

### Creating a New Sampler

To create a new sampler for custom evaluations, you must create a class that
extends the
[`Sampler`](https://github.com/google/adk-python/blob/main/src/google/adk/optimization/sampler.py) base
class.
You must also specify the subclass of [`SamplingResult`](#sampler-results) that
your sampler will use to return eval results.
The sampler must implement the following abstract methods:

* `get_train_example_ids(self)`: Returns the list of example UIDs
to use for optimization.
* `get_validation_example_ids(self)`: Returns the list of example
UIDs to use for validating the optimized agent.
<!-- disableFinding(LINE_OVER_80) -->
* `sample_and_score(self, candidate, example_set, batch, capture_full_eval_data)`:
Evaluates the `candidate` agent on a `batch` of examples from the specified
`example_set` (`"train"` or `"validation"`).
It should return a [`SamplingResult`](#sampler-results) subclass containing the
calculated per-example scores and, if `capture_full_eval_data` is `True`, any
additional data required for eval-guided agent optimization.
You can choose a format for the additional eval data based on your needs by
subclassing `SamplingResult`.
However, the agent optimizer must also support the same subclass of
`SamplingResult`.
The [`UnstructuredSamplingResult`](#sampler-results) implements the simplest
case in which the additional data is stored in a per-example unstructured
dictionary.
<!-- enableFinding(LINE_OVER_80) -->

### Creating a New Agent Optimizer

To create a custom agent optimizer, you must create a class that extends the
[`AgentOptimizer`](https://github.com/google/adk-python/blob/main/src/google/adk/optimization/agent_optimizer.py)
base class.
You must also specify the subclass of [`SamplingResult`](#sampler-results) that
it will accept for eval results and the subclass of
[`AgentWithScores`](#agent-optimizer-results) it will use to represent each
optimized agent and its scores/metrics.
The optimizer must implement the following abstract method:

* `optimize(self, initial_agent, sampler)`: This method orchestrates the
optimization process.
It takes an `initial_agent` to improve and a `sampler` to use for evaluating
candidates.
It should return an [`OptimizerResult`](#agent-optimizer-results) subclass
containing a list of candidate optimized agents along with their scores/metrics
and any overall metrics related to the optimization process.
You can choose a format for the per-candidate scores/metrics based on your needs
by subclassing `AgentWithScores`.
Alternatively you can simply use `AgentWithScores` which allows specifying a
single overall score for each candidate optimized agent.

### Optimizing an Agent Programmatically

The `adk optimize` command uses the [`LocalEvalSampler`](#localevalsampler) and
the [`GEPARootAgentPromptOptimizer`](#geparootagentpromptoptimizer).
When using custom samplers and agent optimizers, you will have to optimize the
agent programmatically.
The following reference code replicates the functionality of the `adk optimize`
command for the above [example](#example).
To use it, create the [dataset](#exampledataset) as shown in the example and run
this code from a Python script within the
[same directory](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world):

```python
import asyncio
import logging
import os

import agent  # the hello_world agent
from google.adk.cli.utils import envs
from google.adk.cli.utils import logs
from google.adk.evaluation.eval_config import EvalConfig
from google.adk.evaluation.local_eval_sets_manager import LocalEvalSetsManager
from google.adk.optimization.gepa_root_agent_prompt_optimizer import GEPARootAgentPromptOptimizer
from google.adk.optimization.gepa_root_agent_prompt_optimizer import GEPARootAgentPromptOptimizerConfig
from google.adk.optimization.local_eval_sampler import LocalEvalSampler
from google.adk.optimization.local_eval_sampler import LocalEvalSamplerConfig

# setup environment variables (API keys, etc.) and logging
envs.load_dotenv_for_agent(".", ".")
logs.setup_adk_logger(logging.INFO)

# create the sampler
sampler_config = LocalEvalSamplerConfig(
    eval_config=EvalConfig(criteria={"response_match_score": 0.75}),
    app_name="hello_world",  # typically the name of the directory containing the agent
    train_eval_set="train_eval_set",  # from the example
)
eval_sets_manager = LocalEvalSetsManager(
    agents_dir=os.path.dirname(os.getcwd()),
)
sampler = LocalEvalSampler(sampler_config, eval_sets_manager)

# create the optimizer
opt_config = GEPARootAgentPromptOptimizerConfig()
optimizer = GEPARootAgentPromptOptimizer(config=opt_config)

# optimize the root agent
initial_agent = agent.root_agent
result = asyncio.run(
    optimizer.optimize(initial_agent, sampler)
)

# show the results
best_idx = result.gepa_result["best_idx"]
print(
    "Validation score:",
    result.optimized_agents[best_idx].overall_score,
    "Optimized prompt:",
    result.optimized_agents[best_idx].optimized_agent.instruction,
    "GEPA metrics:",
    result.gepa_result,
    sep="\n",
)
```
