## Custom Metrics for Agent Evaluation

Supported in ADKPython v1.18.0

If you require specialized metrics tailored to your specific use cases or domains that are not covered by built-in options, you can define your own custom metrics.

## Define a Custom Metric

A custom metric is a Python function that evaluates an agent's performance on a given evaluation case and returns an [`EvaluationResult`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/evaluator.py). The function receives the [`EvalMetric`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_metrics.py), the list of [`Invocation`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_case.py) objects produced by the agent during the evaluation run, and optionally, a list of expected invocations or a [`ConversationScenario`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_case.py) as defined in the eval case.

Each `Invocation` object represents a single turn of interaction between the user and the agent, and contains information such as tool trajectory, intermediate responses, and final response for that turn.

Your custom metric function must have the following signature:

```python
from typing import Optional
from google.adk.evaluation.eval_case import Invocation
from google.adk.evaluation.eval_metrics import EvalMetric
from google.adk.evaluation.conversation_scenarios import ConversationScenario
from google.adk.evaluation.evaluator import EvaluationResult

def my_custom_metric_function(
    eval_metric: EvalMetric,
    actual_invocations: list[Invocation],
    expected_invocations: Optional[list[Invocation]],
    conversation_scenario: Optional[ConversationScenario],
) -> EvaluationResult:
  ...
```

The function should return an `EvaluationResult` object with the `overall_score`, `overall_eval_status`, and `per_invocation_results` fields populated.

### Example

Here is a simple example of a custom metric that checks if the agent's final response in each turn matches the expected final response exactly.

```python
import statistics
from typing import Optional

from google.adk.evaluation.conversation_scenarios import ConversationScenario
from google.adk.evaluation.eval_case import Invocation
from google.adk.evaluation.eval_metrics import EvalMetric
from google.adk.evaluation.eval_metrics import EvalStatus
from google.adk.evaluation.evaluator import EvaluationResult, PerInvocationResult

def check_final_response_exact_match(
    eval_metric: EvalMetric,
    actual_invocations: list[Invocation],
    expected_invocations: Optional[list[Invocation]],
    conversation_scenario: Optional[ConversationScenario],
) -> EvaluationResult:
  """Checks if the final response of the first turn matches the expected
  response."""
  if not expected_invocations:
    return EvaluationResult(overall_score=0.0, overall_eval_status=EvalStatus.NOT_EVALUATED)

  per_invocation_results = []

  for actual, expected in zip(actual_invocations, expected_invocations):
    actual_final_response = "".join([part.text for part in actual.final_response.parts])
    expected_final_response = "".join([part.text for part in expected.final_response.parts])
    score = 1.0 if actual_final_response == expected_final_response else 0.0
    eval_status = EvalStatus.PASSED if score else EvalStatus.FAILED
    invocation_result = PerInvocationResult(
        actual_invocation=actual,
        expected_invocation=expected,
        score=score,
        eval_status=eval_status
    )
    per_invocation_results.append(invocation_result)

  average_score = statistics.mean(result.score for result in per_invocation_results)

  threshold = eval_metric.criterion.threshold
  overall_eval_status = (
    EvalStatus.PASSED if average_score >= threshold else EvalStatus.FAILED
  )
  return EvaluationResult(
      overall_score=average_score,
      overall_eval_status=overall_eval_status,
      per_invocation_results=per_invocation_results,
  )
```

#### Async Metric

If your custom metric needs to make asynchronous calls, such as calling an API, you can define it as an `async` function.

The following is an example of a custom metric function that uses a fake async profanity checker API to check if the agent response contains profanity.

```python
import asyncio
import statistics
from typing import Optional

from google.adk.evaluation.conversation_scenarios import ConversationScenario
from google.adk.evaluation.eval_case import Invocation
from google.adk.evaluation.eval_metrics import EvalMetric
from google.adk.evaluation.eval_metrics import EvalStatus
from google.adk.evaluation.evaluator import EvaluationResult, PerInvocationResult

class ProfanityChecker:
  """A fake profanity checker that mimics an async API."""

  async def check(self, text: str) -> bool:
    """Returns True if profanity is detected, False otherwise."""
    await asyncio.sleep(0.01)
    return "profanity" in text.lower()

profanity_checker = ProfanityChecker()

async def check_for_profanity(
    eval_metric: EvalMetric,
    actual_invocations: list[Invocation],
    expected_invocations: Optional[list[Invocation]],
    conversation_scenario: Optional[ConversationScenario],
) -> EvaluationResult:
  """Checks if the agent response contains profanity using a fake async API."""
  per_invocation_results = []

  for invocation in actual_invocations:
    agent_response = "".join(part.text for part in invocation.final_response.parts)
    has_profanity = await profanity_checker.check(agent_response)
    score = 0.0 if has_profanity else 1.0
    eval_status = EvalStatus.FAILED if has_profanity else EvalStatus.PASSED

    invocation_result = PerInvocationResult(
        actual_invocation=invocation,
        score=score,
        eval_status=eval_status
    )
    per_invocation_results.append(invocation_result)

  scores = [
      result.score
      for result in per_invocation_results
      if result.eval_status != EvalStatus.NOT_EVALUATED
  ]

  average_score = statistics.mean(scores)

  threshold = eval_metric.criterion.threshold
  overall_eval_status = (
      EvalStatus.PASSED if average_score >= threshold else EvalStatus.FAILED
  )
  return EvaluationResult(
      overall_score=average_score,
      overall_eval_status=overall_eval_status,
      per_invocation_results=per_invocation_results,
  )
```

## Use a Custom Metric

To use your custom metric in an evaluation run with `adk eval`, you need to specify it in your `EvalConfig` JSON file.

1. Add your custom metric as one of the eval `criteria`. The key is your metric name, and the value is the passing threshold.
1. Add a `custom_metrics` object to `EvalConfig`. Inside this object, add an entry for each custom metric, where the key is the metric name (matching the one in `criteria`) and the value is an object containing `code_config`.
1. The `code_config` object should contain a `name` field with a string representing the Python import path to your custom metric function, in the format `my.module.my_function`.

### Example `EvalConfig`

Assuming your `check_final_response_match` function is defined in `my_agent.metrics.py`, your `EvalConfig` might look like this:

```json
{
  "criteria": {
    "my_check_final_response_exact_match": {
      "threshold": 0.8
    },
    "tool_trajectory_avg_score": {
      "threshold": 1.0
    }
  },
  "custom_metrics": {
    "my_check_final_response_exact_match": {
      "code_config": {
        "name": "my_agent.metrics.check_final_response_exact_match"
      }
    }
  }
}
```

With this configuration, when you run `adk eval --config_file_path=<path_to_this_config>`, ADK will execute `check_final_response_exact_match` for each eval case, and check if the returned score is >= 0.8 to mark the `response_match` criterion as passed or failed.

### Providing Metric Information

You can optionally provide metadata about your custom metric, such as its description and value range, by adding a [`MetricInfo`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_metrics.py#L369) object within your custom metric definition in `EvalConfig`. If `metric_info` is not provided, ADK will use default values (`min_value`=0.0, `max_value`=1.0).

This information can be used by ADK tools for display and result aggregation purposes.

Here is an example of providing `metric_info` for a custom metric that returns a score between -1.0 and 1.0:

```json
{
  "criteria": {
    "my_metric": {
      "threshold": 0.5
    }
  },
  "custom_metrics": {
    "my_metric": {
      "code_config": {
        "name": "my_agent.metrics.my_metric_function"
      },
      "metric_info": {
        "metric_name": "my_metric",
        "description": "This metric evaluates XYZ and returns a score between -1.0 and 1.0.",
        "metric_value_info": {
          "interval": {
            "min_value": -1.0,
            "max_value": 1.0
          }
        }
      }
    }
  }
}
```
