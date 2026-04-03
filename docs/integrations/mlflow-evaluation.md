---
catalog_title: MLflow Evaluation
catalog_description: Run ADK evaluators as MLflow scorers inside mlflow.genai.evaluate()
catalog_icon: /integrations/assets/mlflow.png
catalog_tags:
  - evaluation
---

# MLflow Evaluation integration for ADK

**Supported in ADK Python**

ADK's built-in evaluators (`ToolTrajectory`, `RougeEvaluator`, etc.) can be used as **MLflow scorers** inside `mlflow.genai.evaluate()`. This lets you combine ADK's deterministic evaluation logic with MLflow's experiment tracking, run comparison, and tracing dashboards — all from a single `evaluate()` call.

This integration is provided by the `mlflow.genai.scorers.google_adk` module, added in [mlflow/mlflow#22299](https://github.com/mlflow/mlflow/pull/22299).

---

## Prerequisites

- MLflow **2.22.0** or newer (the version that ships `mlflow.genai.scorers.google_adk`).
- Google ADK installed in your environment.
- A running MLflow Tracking Server (local or remote).

---

## Install dependencies

```bash
pip install "mlflow>=2.22.0" google-adk
```

---

## Available scorers

| MLflow scorer | Wraps ADK evaluator | What it measures |
|---|---|---|
| `ToolTrajectory` | `TrajectoryEvaluator` | Whether the agent called the right tools in the right order |
| `ResponseMatch` | `RougeEvaluator` | Similarity between the agent's final response and a reference answer |

Both classes live in `mlflow.genai.scorers.google_adk` and accept the same configuration arguments as their underlying ADK evaluators.

---

## Quick start

### 1. Prepare your evaluation dataset

Build a list of evaluation rows. Each row is a dictionary with at minimum a `request` key. Add `expected_response` for `ResponseMatch` and `expected_trajectory` for `ToolTrajectory`.

```python
eval_dataset = [
    {
        "request": "What is 12 + 34?",
        "expected_response": "The answer is 46.",
        "expected_trajectory": [
            {"tool_name": "calculator", "tool_input": {"a": 12, "b": 34}}
        ],
    },
    {
        "request": "What is 100 divided by 4?",
        "expected_response": "The answer is 25.",
        "expected_trajectory": [
            {"tool_name": "calculator", "tool_input": {"a": 100, "b": 4}}
        ],
    },
]
```

### 2. Run evaluation

```python
import mlflow
from mlflow.genai.scorers.google_adk import ToolTrajectory, ResponseMatch

mlflow.set_experiment("adk-agent-eval")

results = mlflow.genai.evaluate(
    data=eval_dataset,
    scorers=[
        ToolTrajectory(match_type="EXACT", threshold=0.5),
        ResponseMatch(threshold=0.6),
    ],
)

print(results.metrics)
```

`mlflow.genai.evaluate()` runs your agent against each row in `eval_dataset`, scores every result with each scorer, and logs the run to your MLflow experiment automatically.

---

## Scorer reference

### `ToolTrajectory`

Wraps ADK's `TrajectoryEvaluator`. Checks that the agent's tool calls match a reference trajectory.

```python
from mlflow.genai.scorers.google_adk import ToolTrajectory

scorer = ToolTrajectory(
    match_type="EXACT",   # "EXACT" or "SUBSET" — see below
    threshold=0.5,        # minimum score (0.0–1.0) to pass
)
```

**`match_type` options:**

| Value | Behaviour |
|---|---|
| `"EXACT"` | The agent's trajectory must match the reference exactly (same tools, same order) |
| `"SUBSET"` | The reference trajectory must be a subset of the agent's actual calls |

The scorer emits a score in `[0.0, 1.0]` per row, where `1.0` means a perfect match.

---

### `ResponseMatch`

Wraps ADK's `RougeEvaluator`. Computes ROUGE-L similarity between the agent's response and an `expected_response` reference.

```python
from mlflow.genai.scorers.google_adk import ResponseMatch

scorer = ResponseMatch(
    threshold=0.6,   # minimum ROUGE-L score (0.0–1.0) to pass
)
```

The scorer emits a score in `[0.0, 1.0]` per row.

---

## Full example with an ADK agent

The example below wires a real ADK agent into `mlflow.genai.evaluate()`.

```python
import mlflow
from mlflow.genai.scorers.google_adk import ToolTrajectory, ResponseMatch

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.adk.runners import InMemoryRunner


# --- Define the agent ---

def calculator(a: float, b: float) -> str:
    """Add two numbers and return the result."""
    return str(a + b)


calculator_tool = FunctionTool(func=calculator)

agent = LlmAgent(
    name="MathAgent",
    model="gemini-2.0-flash-exp",
    instruction=(
        "You are a helpful assistant that can do math. "
        "Use the calculator tool whenever you are asked to add two numbers."
    ),
    tools=[calculator_tool],
)

runner = InMemoryRunner(agent=agent)


# --- Define a predict function for mlflow.genai.evaluate ---

def predict(inputs: dict) -> dict:
    """Run the agent and return its response and tool trajectory."""
    result = runner.run(inputs["request"])
    return {
        "response": result.text,
        "trajectory": result.tool_calls,   # list of {tool_name, tool_input} dicts
    }


# --- Evaluation dataset ---

eval_dataset = [
    {
        "request": "What is 12 + 34?",
        "expected_response": "The answer is 46.",
        "expected_trajectory": [
            {"tool_name": "calculator", "tool_input": {"a": 12, "b": 34}}
        ],
    },
    {
        "request": "What is 7 + 93?",
        "expected_response": "The answer is 100.",
        "expected_trajectory": [
            {"tool_name": "calculator", "tool_input": {"a": 7, "b": 93}}
        ],
    },
]


# --- Run evaluation ---

mlflow.set_experiment("math-agent-eval")

results = mlflow.genai.evaluate(
    predict_fn=predict,
    data=eval_dataset,
    scorers=[
        ToolTrajectory(match_type="EXACT", threshold=0.5),
        ResponseMatch(threshold=0.6),
    ],
)

print(results.metrics)
# {
#   "tool_trajectory/mean": 1.0,
#   "response_match/mean": 0.87,
#   ...
# }
```

---

## View results in the MLflow UI

Open the MLflow UI at `http://localhost:5000` (or your server address), navigate to the **math-agent-eval** experiment, and select the run. Each scorer appears as a metric column so you can compare runs side by side as you iterate on your agent.

---

## Combining with MLflow tracing

If you have the [MLflow tracing integration](./mlflow.md) already configured, ADK will emit OpenTelemetry spans **during** the evaluation run. Those spans are automatically linked to the evaluation run in the MLflow UI, giving you a unified view of scores and execution traces for every row.

No extra configuration is required — just make sure your OTLP exporter and tracer provider are initialised before the `mlflow.genai.evaluate()` call, as described in the [tracing guide](./mlflow.md#configure-opentelemetry-required).

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'mlflow.genai.scorers.google_adk'`**
Upgrade MLflow to the version that includes the ADK scorer module (`pip install --upgrade mlflow`).

**Scores are always `0.0` for `ToolTrajectory`**
Check that your `predict` function returns a `trajectory` key whose values match the `{"tool_name": ..., "tool_input": ...}` schema expected by ADK's `TrajectoryEvaluator`.

**`ResponseMatch` scores are lower than expected**
`ResponseMatch` uses ROUGE-L, which is sensitive to wording. If your agent paraphrases the expected response, consider lowering `threshold` or switching to a model-based scorer for semantic similarity.

---

## Resources

- [MLflow Evaluation documentation](https://mlflow.org/docs/latest/llms/llm-evaluate/index.html)
- [ADK built-in evaluators](../evaluate/index.md)
- [MLflow tracing integration for ADK](./mlflow.md)
- [MLflow PR #22299 — Add Google ADK scorers](https://github.com/mlflow/mlflow/pull/22299)
