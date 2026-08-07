# MLflow scorers for ADK agents

Supported in ADKPython

[MLflow](https://mlflow.org/docs/latest/genai/eval-monitor/) wraps five ADK evaluators as third-party scorers so you can use ADK's trajectory matching, ROUGE response similarity, and LLM-judge metrics inside any `mlflow.genai.evaluate()` run. The integration covers ADK's `TrajectoryEvaluator`, `RougeEvaluator`, `FinalResponseMatchV2Evaluator`, `SafetyEvaluatorV1`, and `HallucinationsV1Evaluator`.

If you're also tracing your ADK agent, see the [MLflow Tracing integration](/integrations/mlflow-tracing/) for one-line OTel auto-tracing setup. The deterministic scorers below read tool calls directly from those traces.

## Use cases

- **Tool trajectory evaluation**: Verify the agent called the right tools in the right order, with `EXACT`, `IN_ORDER`, or `ANY_ORDER` matching.
- **Response similarity**: Score the agent's final response against a reference answer using ROUGE-1 F-measure.
- **LLM-judged response quality**: Use Gemini to score whether the agent's response matches an expected response semantically, with majority voting.
- **Hallucination detection**: Use Gemini to score whether the agent's response contains fabricated facts.
- **Safety checks**: Use Vertex AI's prebuilt SAFETY metric to flag unsafe output without managing a judge model.
- **Mix-and-match scoring**: Run deterministic scorers alongside LLM judges in a single `mlflow.genai.evaluate()` call, layering cheap structural checks under more expensive judge calls.

## Prerequisites

- MLflow 3.13 or newer for the full scorer set. MLflow 3.11 ships the two deterministic scorers; the three LLM-judge scorers landed in 3.13.
- ADK installed in your environment.
- For the LLM-judge scorers: a `GEMINI_API_KEY` (Gemini Developer API) or Google Cloud project credentials (Vertex AI). `Safety` always requires the Vertex AI path because it delegates to a managed metric.

## Install dependencies

```bash
pip install "mlflow>=3.13" google-adk
```

## Available scorers

The five MLflow scorers, grouped by how they score:

| Scorer               | What it evaluates                                                                 | Wraps                                   |
| -------------------- | --------------------------------------------------------------------------------- | --------------------------------------- |
| `ToolTrajectory`     | Whether the agent called the right tools in the right order                       | `TrajectoryEvaluator`                   |
| `ResponseMatch`      | Lexical similarity between actual and expected response (ROUGE-1 F-measure)       | `RougeEvaluator`                        |
| `ResponseEvaluation` | Whether the final response matches the expected response semantically (LLM judge) | `FinalResponseMatchV2Evaluator`         |
| `Safety`             | Whether the response contains unsafe content                                      | `SafetyEvaluatorV1` (Vertex AI managed) |
| `Hallucination`      | Whether the response contains hallucinated content (LLM judge)                    | `HallucinationsV1Evaluator`             |

`ToolTrajectory` and `ResponseMatch` run in microseconds and have no API cost. `ResponseEvaluation` and `Hallucination` call a default Gemini Flash judge model with five-sample majority voting; both the model and sample count are configurable. `Safety` is the exception. It routes through Vertex AI's prebuilt SAFETY metric, which manages its own model selection, so the scorer raises `TypeError` if you pass `model` or `num_samples`.

## Quick start

Call a scorer directly:

```python
from mlflow.genai.scorers.google_adk import ToolTrajectory

scorer = ToolTrajectory(match_type="EXACT", threshold=0.5)
feedback = scorer(
    inputs="Book a flight to Paris",
    outputs="Booked flight AA123 to Paris",
    expectations={
        "expected_tool_calls": [
            {"name": "search_flights", "args": {"destination": "Paris"}},
            {"name": "book_flight", "args": {"flight_id": "AA123"}},
        ],
        "actual_tool_calls": [
            {"name": "search_flights", "args": {"destination": "Paris"}},
            {"name": "book_flight", "args": {"flight_id": "AA123"}},
        ],
    },
)

print(feedback.value)            # "yes" or "no"
print(feedback.metadata["score"]) # 1.0 on a full match
```

Or compose multiple scorers in a single evaluation:

```python
import mlflow
from mlflow.genai.scorers.google_adk import (
    ToolTrajectory,
    ResponseMatch,
    ResponseEvaluation,
)

eval_data = [
    {
        "inputs": {"query": "Find me a flight to Paris next Friday."},
        "outputs": "I found 3 flights to Paris on Friday: AA101, DL202, UA303.",
        "expectations": {
            "expected_tool_calls": [
                {"name": "search_flights", "args": {"destination": "Paris"}},
            ],
            "actual_tool_calls": [
                {"name": "search_flights", "args": {"destination": "Paris"}},
            ],
            "expected_response": "Here are flights to Paris next Friday.",
        },
    },
]

results = mlflow.genai.evaluate(
    data=eval_data,
    scorers=[
        ToolTrajectory(match_type="EXACT", threshold=0.5),
        ResponseMatch(threshold=0.5),
        ResponseEvaluation(threshold=0.6),
    ],
)
```

## How tool calls are resolved

`ToolTrajectory` needs both the expected tool calls (from `expectations["expected_tool_calls"]`) and the actual tool calls the agent made. It resolves the actual calls in this order:

1. `expectations["actual_tool_calls"]` when present. Useful for offline evaluation where you've captured tool calls as data.
1. `TOOL` spans on the MLflow trace. When no explicit override is provided, the scorer walks the trace and reads tool calls from spans tagged as `TOOL`. This is the path for live evaluations that pass a trace directly or use `mlflow.genai.evaluate(predict_fn=...)`.
1. Empty list. If neither is available, the scorer compares the expected list against an empty actual list, which results in a 0.0 score for non-empty expectations.

Pair this with the [MLflow Tracing integration](/integrations/mlflow-tracing/) for a fully online setup: ADK emits OTel spans during agent execution, MLflow ingests them, and the scorers read tool calls back out of the trace without any explicit data plumbing.

## LLM-judge configuration

`ResponseEvaluation` and `Hallucination` take a Gemini model ID, a pass/fail threshold, and a sample count for majority voting:

```python
from mlflow.genai.scorers.google_adk import Hallucination, ResponseEvaluation

response_eval = ResponseEvaluation(
    model="gemini-flash-latest",
    threshold=0.5,
    num_samples=5,
)

hallucination = Hallucination(model="gemini-flash-latest", threshold=0.5)
```

The model must be a name that ADK's `LlmRegistry` can resolve, such as `gemini-flash-latest` or `gemini-pro-latest`. MLflow model URIs like `databricks` or `openai:/gpt-4o` aren't supported here because ADK's evaluators wire directly into Google's model registry.

`Safety` runs through Vertex AI's managed SAFETY metric. It requires `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, and `gcloud auth application-default login` (or a service account):

```python
from mlflow.genai.scorers.google_adk import Safety

safety = Safety(threshold=0.5)
```

When auth is missing, the LLM-judge scorers return a `Feedback` with an `error` field rather than raising. Evaluation runs continue and surface the misconfiguration per sample.

## Resources

- [MLflow ADK scorer documentation](https://mlflow.org/docs/latest/genai/eval-monitor/scorers/third-party/google-adk/)
- [MLflow Tracing integration for ADK](/integrations/mlflow-tracing/)
- [MLflow AI Gateway for ADK](/integrations/mlflow-gateway/)
- [ADK Evaluation Guide](/evaluate/)
- [MLflow on GitHub](https://github.com/mlflow/mlflow)
