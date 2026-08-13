---
catalog_title: tracegauge Cost Evaluator
catalog_description: Per-invocation dollar cost alongside ADK's quality metrics
catalog_icon: /integrations/assets/adk-tracegauge.png
catalog_tags: ["evaluation"]
---

# tracegauge Cost Evaluator for ADK agents

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[`adk-tracegauge`](https://github.com/gaurav-gandhi-2411/adk-tracegauge) registers a
`google.adk.evaluation` metric that reports real dollar cost per invocation, built on
[tracegauge](https://github.com/gaurav-gandhi-2411/token-efficiency-scorer)'s cost engine.
ADK's built-in evaluation metrics report quality — trajectory match, response similarity,
safety, hallucination — but none of them report cost or token usage. This fills exactly
that gap.

> **Requires an `App` with the plugin attached.** ADK's `Invocation` objects never carry
> token usage or model identity — that data only exists on the `LlmResponse` a plugin sees
> during inference. If you evaluate against a bare `root_agent` with no `App`, ADK's eval
> harness never fires plugins at all, and this metric reports `no usage captured` for every
> invocation. See [Use with agent](#use-with-agent) below — this is not optional.

## Use cases

- **Cost regression gates**: Fail CI when a prompt or model change measurably increases
  cost per task, the same way you'd gate on a quality regression.
- **Model/config comparison**: Compare real dollar cost across model choices
  (`gemini-2.5-flash` vs. `gemini-2.5-pro`) or prompt variants on the same eval set.
- **Budget tracking during development**: See per-invocation cost alongside quality metrics
  in the same `adk eval` run, without a separate cost-tracking pass.

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

## Use with agent

```python
from adk_tracegauge import TraceGaugeUsagePlugin
from google.adk.agents import Agent
from google.adk.apps import App

root_agent = Agent(
    name="assistant",
    model="gemini-2.5-flash",
    instruction="You are a helpful assistant.",
)

# The plugin is what makes cost data visible to the evaluator at all --
# see the note above.
app = App(name="my_app", root_agent=root_agent, plugins=[TraceGaugeUsagePlugin()])
```

Reference `adk_tracegauge_cost_usd` as a `metric_name` in your eval config, and make sure
`AgentEvaluator` picks up this `app` (it looks for an `app` attribute in your agent module
automatically).

## Available metrics

| Metric | What it reports |
| ---- | ---- |
| `adk_tracegauge_cost_usd` | Dollar cost of one invocation, summed across every real model call within it (tool loops and sub-agent delegation can mean more than one call per invocation). Raw USD in `score`, a per-call token/cost breakdown in the result's rationale. |

This metric always reports `NOT_EVALUATED` as its `eval_status` — ADK's built-in pass/fail
convention (`score >= threshold → PASSED`) is hardcoded higher-is-better, and cost is
lower-is-better with no inverted-metric convention to plug into. Read `score` directly, or
write your own threshold comparison against it.

Reports raw counts and dollars only — no calibrated efficiency bands. tracegauge's own
token-economy baselines are derived from Claude Code sessions; applying them to ADK agent
behavior would be an unvalidated transfer. An invocation whose model isn't in the bundled
Gemini price table reports `score=None` naming the specific unresolved model, never a
number computed from a fallback rate.

## Resources

- [GitHub repository](https://github.com/gaurav-gandhi-2411/adk-tracegauge): source code,
  issues, and the full design rationale in `README.md`.
- [PyPI package](https://pypi.org/project/adk-tracegauge/): releases and install
  instructions.
- [tracegauge](https://github.com/gaurav-gandhi-2411/token-efficiency-scorer): the
  underlying cost-computation engine this package depends on.
- [ADK Evaluation Guide](/evaluate/): background on ADK's evaluation framework and the
  `MetricEvaluatorRegistry` this package registers against.
