---
catalog_title: tracegauge Cost Evaluator
catalog_description: Real per-invocation dollar cost for custom ADK eval harnesses
catalog_icon: /integrations/assets/adk-tracegauge.png
catalog_tags: ["evaluation"]
---

# tracegauge Cost Evaluator for ADK agents

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[`adk-tracegauge`](https://github.com/gaurav-gandhi-2411/adk-tracegauge) is a cost
evaluator for **custom** ADK eval harnesses: it captures real per-invocation token usage
during inference and turns it into a dollar-cost `PerInvocationResult`, built on
[tracegauge](https://github.com/gaurav-gandhi-2411/token-efficiency-scorer)'s cost engine.
ADK's built-in evaluation metrics report quality — trajectory match, response similarity,
safety, hallucination — but none of them report cost or token usage. This fills that gap,
with one significant caveat below.

> **Not a drop-in `adk eval`/`AgentEvaluator` metric.** `LocalEvalService` discards
> per-invocation results for any metric whose `eval_status` is `NOT_EVALUATED` — the
> permanent status of this metric, since cost is lower-is-better and has no honest fit in
> ADK's `score >= threshold -> PASSED` convention. In practice: `AgentEvaluator.evaluate()`
> raises unconditionally when this metric is registered, and `adk eval` silently discards
> its per-invocation score/rationale. Filed upstream as a design question:
> [google/adk-python#6725](https://github.com/google/adk-python/issues/6725). Until that's
> resolved, use this package through a hand-rolled `Runner` harness you drive yourself —
> see [Use with a custom eval harness](#use-with-a-custom-eval-harness) below, and the
> package README for the full worked example.

## Use cases

- **Cost regression checks in a custom harness**: Compute real dollar cost per invocation
  in your own eval script or CI job, and fail the build when a prompt or model change
  measurably increases cost.
- **Model/config comparison**: Compare real dollar cost across model choices
  (`gemini-2.5-flash` vs. `gemini-2.5-pro`) or prompt variants, driven yourself outside
  ADK's built-in eval runner.
- **Ad hoc budget checks during development**: Wire the plugin into your own `App` and
  read cost straight out of `CostEfficiencyEvaluator.evaluate_invocations()` while
  iterating on a prompt or agent design.

## Prerequisites

- Python 3.10 or later
- `google-adk[eval]` — the `[eval]` extra is required, not optional (see
  [Installation](#installation))
- A Gemini model (`gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-2.5-flash-lite`, or
  `gemini-3.x` family) — the bundled price table is Gemini-only

## Installation

```bash
pip install adk-tracegauge
```

`google-adk[eval]` and `tracegauge` are pulled in as dependencies. The `[eval]` extra is
required: `google-adk`'s own evaluator registry unconditionally imports every built-in
evaluator at module load time, including ones that need `pandas`/`jinja2`/`rouge-score` —
without the extra, `import adk_tracegauge` fails with `ModuleNotFoundError: No module named
'pandas'`.

## Use with a custom eval harness

`adk eval` and `AgentEvaluator.evaluate()` build their own internal `Runner` from a bare
`root_agent` and never look at any `App`/plugins you define (confirmed against
`google-adk==2.6.3`) — so wiring the plugin into an `App` only works if you build and drive
the `Runner` yourself:

```python
from adk_tracegauge import CostEfficiencyEvaluator, TraceGaugeUsagePlugin
from adk_tracegauge.evaluator import METRIC_NAME
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.evaluation.eval_metrics import EvalMetric
from google.adk.evaluation.evaluation_generator import EvaluationGenerator
from google.adk.runners import InMemoryRunner

root_agent = Agent(name="assistant", model="gemini-2.5-flash", instruction="...")
app = App(name="my_app", root_agent=root_agent, plugins=[TraceGaugeUsagePlugin()])
runner = InMemoryRunner(app=app)

session = await runner.session_service.create_session(app_name=app.name, user_id="eval_user")
events = [e async for e in runner.run_async(
    user_id="eval_user", session_id=session.id, new_message=user_message,
)]

# EvaluationGenerator.convert_events_to_eval_invocations is the internal ADK helper
# LocalEvalService itself uses for this -- not public API, no stability guarantee.
invocations = EvaluationGenerator.convert_events_to_eval_invocations(events)

evaluator = CostEfficiencyEvaluator(eval_metric=EvalMetric(metric_name=METRIC_NAME))
result = evaluator.evaluate_invocations(invocations)
print(result.per_invocation_results[0].score)  # real dollar cost, read directly
```

Full six-step worked example, including what you lose by not going through
`AgentEvaluator`/`adk eval` (other built-in metrics, `eval_history/` persistence,
`num_runs`, parallelism): see the package
[README](https://github.com/gaurav-gandhi-2411/adk-tracegauge#the-only-path-that-reliably-works-a-hand-rolled-runner-harness).

A narrower, caveated workaround exists for getting a single aggregate cost figure to show
up in an `adk eval` console run — attaching the plugin's callback directly via
`LlmAgent(after_model_callback=...)` instead of an `App`. It does not fix
`AgentEvaluator.evaluate()` (still raises) and still discards per-invocation detail; see
the README's "Documented workaround" section before relying on it.

## Available metrics

| Metric | What it reports |
| ---- | ---- |
| `adk_tracegauge_cost_usd` | Dollar cost of one invocation, summed across every real model call within it (tool loops and sub-agent delegation can mean more than one call per invocation). Raw USD in `score`, a per-call token/cost breakdown in the result's rationale (and, going through ADK's own eval runner, in a `warnings.warn` at evaluate time — see the note above). |

This metric always reports `NOT_EVALUATED` as its `eval_status` — ADK's built-in pass/fail
convention (`score >= threshold → PASSED`) is hardcoded higher-is-better, and cost is
lower-is-better with no inverted-metric convention to plug into. Read `score` directly
from the harness above, or write your own threshold comparison against it — never rely on
ADK's built-in pass/fail gate to expose it (see [google/adk-python#6725](https://github.com/google/adk-python/issues/6725)).

Reports raw counts and dollars only — no calibrated efficiency bands. tracegauge's own
token-economy baselines are derived from Claude Code sessions; applying them to ADK agent
behavior would be an unvalidated transfer. An invocation whose model isn't in the bundled
Gemini price table reports `score=None` naming the specific unresolved model, never a
number computed from a fallback rate.

## Resources

- [GitHub repository](https://github.com/gaurav-gandhi-2411/adk-tracegauge): source code,
  the full hand-rolled-harness worked example, and design rationale in `README.md`.
- [google/adk-python#6725](https://github.com/google/adk-python/issues/6725): the upstream
  design question this integration's limitations are filed against.
- [PyPI package](https://pypi.org/project/adk-tracegauge/): releases and install
  instructions.
- [tracegauge](https://github.com/gaurav-gandhi-2411/token-efficiency-scorer): the
  underlying cost-computation engine this package depends on.
- [ADK Evaluation Guide](/evaluate/): background on ADK's evaluation framework and the
  `MetricEvaluatorRegistry` this package registers against.
