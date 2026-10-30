## Custom Metrics for Agent Evaluation

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.18.0</span>
</div>

If you require specialized metrics tailored to your specific use cases or
domains that are not covered by built-in options, you can define your own
custom metrics.

Use a function for metrics that score invocations. For metrics that also need
session state, see [Evaluate session state](#evaluate-session-state).

## Define a Custom Metric

A custom metric is a Python function that evaluates an agent's performance on a
given evaluation case and returns an
[`EvaluationResult`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/evaluator.py).
The function receives the [`EvalMetric`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_metrics.py),
the list of [`Invocation`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_case.py)
objects produced by the agent during the evaluation run, and optionally, a list
of expected invocations or a
[`ConversationScenario`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_case.py)
as defined in the eval case.

Each `Invocation` object represents a single turn of interaction between the
user and the agent, and contains information such as tool trajectory,
intermediate responses, and final response for that turn.

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

The function should return an `EvaluationResult` object with the
`overall_score`, `overall_eval_status`, and `per_invocation_results` fields
populated.

### Example

Here is a simple example of a custom metric that checks if the agent's final
response in each turn matches the expected final response exactly.

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

If your custom metric needs to make asynchronous calls, such as calling an API,
you can define it as an `async` function.

The following is an example of a custom metric function that uses a fake async
profanity checker API to check if the agent response contains profanity.

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

To use your custom metric in an evaluation run with `adk eval`, you need to
specify it in your `EvalConfig` JSON file.

1.  Add your custom metric as one of the eval `criteria`. The key is your metric
    name, and the value is the passing threshold.
2.  Add a `custom_metrics` object to `EvalConfig`. Inside this object, add an
    entry for each custom metric, where the key is the metric name (matching the
    one in `criteria`) and the value is an object containing `code_config`.
3.  The `code_config` object should contain a `name` field with a string
    representing the Python import path to your custom metric function, in the
    format `my.module.my_function`.

### Example `EvalConfig`

Assuming your `check_final_response_exact_match` function is defined in
`my_agent.metrics.py`, your `EvalConfig` might look like this:

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

With this configuration, when you run
`adk eval --config_file_path=<path_to_this_config>`, ADK will execute
`check_final_response_exact_match` for each eval case, and check if the returned
score is >= 0.8 to mark the `my_check_final_response_exact_match` criterion as
passed or failed.

### Providing Metric Information

You can optionally provide metadata about your custom metric, such as its
description and value range, by adding a [`MetricInfo`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_metrics.py#L369) object within your
custom metric definition in `EvalConfig`. If `metric_info` is not provided,
ADK will use default values (`min_value`=0.0, `max_value`=1.0).

This information can be used by ADK tools for display and result aggregation
purposes.

Here is an example of providing `metric_info` for a custom metric that returns
a score between -1.0 and 1.0:

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

## Evaluate session state

!!! note "Proposed API"

    This API is proposed for
    [adk-python issue #4532](https://github.com/google/adk-python/issues/4532).
    It is not available in a released version of ADK.

To check the state an agent changes, subclass `Evaluator` and override
`evaluate_with_context`. The method receives an `EvaluationContext` with three
optional dictionaries:

| Field | Source |
| --- | --- |
| `initial_session_state` | Actual state before the first turn. |
| `final_session_state` | Actual state after the last turn. |
| `expected_final_session_state` | `final_session_state` from the eval case. |

ADK captures the actual states during inference and saves them with the inference
result. Later session updates do not change those snapshots. For an existing
session, the initial snapshot is its actual state, which can differ from the
`session_input.state` seed for a new session. Each metric receives its own copy.

A field is `None` when the state is unavailable. Old inference results without
snapshots also use `None`; ADK does not fill those fields from the live session.
An empty dictionary is valid state, so check `is None` to detect absent data.

The expected state preserves the eval case value, whose default is `{}`. If you
omit `final_session_state`, the expected state is empty. Set it to `null` in JSON
or `None` in Python when no expected state is available.

The following evaluator checks whether the final state exactly matches the
expected state. It returns `NOT_EVALUATED` if either state is absent. ADK requires
one result per actual invocation, so the example repeats the case-level score
for each invocation.

```python
from google.adk.evaluation import EvaluationContext
from google.adk.evaluation.eval_metrics import EvalMetric
from google.adk.evaluation.eval_metrics import EvalStatus
from google.adk.evaluation.evaluator import EvaluationResult
from google.adk.evaluation.evaluator import Evaluator
from google.adk.evaluation.evaluator import PerInvocationResult


class FinalStateMatchEvaluator(Evaluator):
  """Scores 1.0 when the final state matches the expected state."""

  def __init__(self, eval_metric: EvalMetric):
    if eval_metric.criterion is not None:
      self._threshold = eval_metric.criterion.threshold
    elif eval_metric.threshold is not None:
      self._threshold = eval_metric.threshold
    else:
      raise ValueError("final_state_match requires a threshold.")

  def evaluate_with_context(
      self,
      actual_invocations,
      expected_invocations=None,
      conversation_scenario=None,
      *,
      context: EvaluationContext,
  ) -> EvaluationResult:
    actual = context.final_session_state
    expected = context.expected_final_session_state
    if actual is None or expected is None or not actual_invocations:
      return EvaluationResult()

    score = 1.0 if actual == expected else 0.0
    status = (
        EvalStatus.PASSED if score >= self._threshold else EvalStatus.FAILED
    )
    return EvaluationResult(
        overall_score=score,
        overall_eval_status=status,
        per_invocation_results=[
            PerInvocationResult(
                actual_invocation=invocation, score=score, eval_status=status
            )
            for invocation in actual_invocations
        ],
    )
```

Register the class before a programmatic evaluation run, in the same process:

```python
from google.adk.evaluation.eval_metrics import Interval
from google.adk.evaluation.eval_metrics import MetricInfo
from google.adk.evaluation.eval_metrics import MetricValueInfo
from google.adk.evaluation.metric_evaluator_registry import (
    DEFAULT_METRIC_EVALUATOR_REGISTRY,
)

DEFAULT_METRIC_EVALUATOR_REGISTRY.register_evaluator(
    metric_info=MetricInfo(
        metric_name="final_state_match",
        description="Checks the expected final session state.",
        metric_value_info=MetricValueInfo(
            interval=Interval(min_value=0.0, max_value=1.0)
        ),
    ),
    evaluator=FinalStateMatchEvaluator,
)
```

Then add the metric to `criteria`. A class already in the registry does not need
a `custom_metrics` entry:

```json
{
  "criteria": {
    "final_state_match": {"threshold": 1.0}
  }
}
```

For example, set `final_session_state` to `{"order_status": "confirmed"}` in the
eval case to require exactly that final state. `AgentEvaluator` retains custom
class registrations from the default registry. A standalone `adk eval` command
cannot load a class through `custom_metrics.code_config`; that option accepts a
function path.

An override of `evaluate_with_context` may also be async. Existing evaluators
that only implement `evaluate_invocations` need no changes. Custom metric
functions keep their four-argument signature.
