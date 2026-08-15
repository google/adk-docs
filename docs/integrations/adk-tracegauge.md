---
catalog_title: adk-tracegauge Cost Regression Gate
catalog_description: CI cost-regression gate plus a real per-invocation dollar-cost metric for ADK evals
catalog_icon: /integrations/assets/adk-tracegauge.png
catalog_tags: ["evaluation"]
---

# adk-tracegauge Cost Regression Gate for ADK agents

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[`adk-tracegauge`](https://github.com/gaurav-gandhi-2411/adk-tracegauge) is a
statistically-validated **CI cost-regression gate** for ADK agents: snapshot a real
per-invocation USD cost distribution from an eval run, and fail the build only when a cost
increase is both statistically and practically significant. It also registers a real
per-invocation **PASS/FAIL dollar-cost threshold metric** inside `adk eval` itself — useful
for inline cost visibility while iterating, and complementary to (not a replacement for) the
CI gate.

ADK's built-in evaluation metrics report quality — trajectory match, response similarity,
safety, hallucination — but none of them report cost. This fills that gap.

> **The CI gate (`adk-tracegauge check`) is the primary, recommended path — not the `adk eval`
> metric below.** `adk eval`'s own process exit code does not reflect PASSED/FAILED (see
> [Known ADK-side limitations](#known-adk-side-limitations)), so it cannot gate a CI job on
> its own; `adk-tracegauge check` has its own real, distinguishable exit codes and is proven to
> work standalone. See [Use with agent](#use-with-agent) below — the metric path still
> requires the plugin to be wired in either way.

## Use cases

- **Cost regression gates (primary)**: `adk-tracegauge check` fails CI when a prompt or model
  change measurably increases mean cost per invocation, using a percentile bootstrap — not
  a naive point-estimate delta — so a build doesn't fail on noise.
- **Inline cost visibility during eval iteration**: the `adk_tracegauge_cost_usd` metric
  reports a real dollar score and PASSED/FAILED verdict per invocation directly in `adk eval`
  output, against a threshold you set.
- **Model/config comparison**: compare real dollar cost across model choices
  (`gemini-2.5-flash` vs. `gemini-2.5-pro`) or prompt variants on the same eval set.

## Prerequisites

- Python 3.10 or later
- `google-adk[eval]>=2.6.0,<2.8.0` — the `[eval]` extra is required, not optional (see
  [Installation](#installation))
- A priced model: any current-generation **Gemini** model (ADK's native backend), or
  **Claude**/**GPT** reached through ADK's `LiteLlm` integration (e.g.
  `model="anthropic/claude-opus-5"`), or a **local/self-hosted** model (Ollama, vLLM) with an
  explicit opt-in — see [Available metrics](#available-metrics) for the full pricing scope
  and how unresolved models are handled.

## Installation

```bash
pip install adk-tracegauge
```

`google-adk[eval]` is pulled in as a dependency; `adk-tracegauge` has no other required
runtime dependency (its dollar-cost arithmetic is implemented in-house — it does not depend
on any external cost-computation library). The `[eval]` extra is required: `google-adk`'s
own evaluator registry unconditionally imports every built-in evaluator at module load time,
including ones that need `pandas`/`jinja2`/`rouge-score` — without the extra, `import
adk_tracegauge` fails with `ModuleNotFoundError: No module named 'pandas'`.

## Use with agent

The plugin has to capture real token usage before either path (the CLI gate or the `adk
eval` metric) has anything to price. Wire `after_model_callback` directly onto your agent —
this is the only integration code either path needs:

```python
from google.adk.agents.llm_agent import LlmAgent

import adk_tracegauge  # registers the adk_tracegauge_cost_usd metric as an import side effect
from adk_tracegauge import TraceGaugeUsagePlugin

_usage_plugin = TraceGaugeUsagePlugin()

root_agent = LlmAgent(
    name="assistant",
    model="gemini-2.5-flash",
    instruction="You are a helpful assistant.",
    after_model_callback=_usage_plugin.after_model_callback,
)
```

This works with the standard `adk eval` CLI directly — no `App`/plugin-list wiring needed
for the primary paths (`adk-tracegauge check` or the `adk eval` metric). A separate,
hand-rolled `App(plugins=[...])` harness is only needed for the optional sub-agent
cost-rollup pattern described in the project's own README — out of scope for this page.

## The CI cost-regression gate: `adk-tracegauge check`

`adk-tracegauge` (the console script this package installs) has two subcommands: `snapshot`
(persist a `UsageStore`'s priced invocations to a JSON file) and `check` (a percentile
bootstrap comparing two snapshots). Write a zero-argument entrypoint that runs your eval —
`AgentEvaluator.evaluate()`, a real `adk eval` CLI invocation, or your own harness — with
the plugin wired in per the previous section, then:

```bash
adk-tracegauge snapshot --entrypoint my_eval_suite:run_and_return_store --output baseline.json
adk-tracegauge snapshot --entrypoint my_eval_suite:run_and_return_store --output current.json
adk-tracegauge check --baseline baseline.json --current current.json
```

`adk-tracegauge check` exits `0` (no significant regression), `1` (regression: the cost
increase is both statistically significant — the bootstrap confidence interval excludes
zero — and clears a configurable practical-significance floor), or `3` (insufficient
data — fewer than `--min-n`, default 30, priced invocations in either snapshot; a bootstrap
CI is not statistically meaningful below that). Every run also prints its own **achieved
statistical power** — the smallest cost increase the bootstrap test could reliably (80%
power) have detected given that run's own observed variance and sample size — with an
explicit warning whenever your configured significance floor is smaller than that
achievable figure. See the project's own README ("Known limitations") for the full,
honestly-reported detection-power numbers this estimate is validated against.

### Paired mode: the default, whenever a pairing key resolves

At a realistic ADK eval-set size (tens of cases, not hundreds), an unpaired two-sample
comparison can be substantially underpowered. `adk-tracegauge check` defaults to
`--mode auto`, and that default **prefers a paired bootstrap** — the same before/after eval
case compared against itself, cancelling case-to-case cost variance rather than averaging
over it — whenever a stable pairing key resolves with at least `--min-n` (default 30)
overlapping cases between the two snapshots. Paired mode is dramatically more sensitive at
the same `n` whenever real per-case cost variance exists; **only when no such key
resolves, or too few cases overlap, does `check` automatically fall back to the two-sample
comparison** — never silently: the resolved mode and key are printed on every run.

Pairing needs a stable key that identifies "the same eval case" across both runs. For the
standard `adk eval` CLI workflow, that key is each case's own authored `eval_id` from the
`.evalset.json` file, recovered by pointing `adk-tracegauge snapshot --eval-history` at the
`.evalset_result.json` file `adk eval` writes after every run. No flag is needed to opt in —
`--mode auto` finds and uses this key automatically; `--mode paired`/`--mode two-sample`
remain available to force one method by name (`--mode paired` fails loudly, naming the
actual overlap count, rather than silently falling back, if too few cases match).

**One real detail that matters here:** `after_model_callback` only ever populates an
in-memory store — it does not survive a plain shell `adk eval` process exiting. So the
entrypoint your `adk-tracegauge snapshot` command runs must invoke the same underlying
evaluation call *in-process* (via `click.testing.CliRunner` against `cli_eval`, the exact
function `adk eval` itself runs), not shell out to `adk eval` as a separate step — otherwise
the snapshot step sees an empty store. A minimal entrypoint that does this correctly:

```python
# my_eval_suite.py
from __future__ import annotations

from pathlib import Path

_EVAL_SET = "eval_data/my_eval_set.evalset.json"
_CONFIG = "test_config.json"


def _run_adk_eval_in_process(agent_dir: str, dest: str) -> None:
    from click.testing import CliRunner
    from google.adk.cli.cli_tools_click import cli_eval

    history_dir = Path(agent_dir) / ".adk" / "eval_history"
    for f in history_dir.glob("*.evalset_result.json"):
        f.unlink()  # start from a clean slate so exactly one new file exists after

    result = CliRunner().invoke(
        cli_eval, [agent_dir, _EVAL_SET, "--config_file_path", _CONFIG], catch_exceptions=False
    )
    if result.exit_code != 0:
        raise RuntimeError(f"adk eval failed:\n{result.output}")

    # adk eval names this file with a timestamp -- copy it to a fixed,
    # predictable path so --eval-history below can name it ahead of time.
    [new_file] = sorted(history_dir.glob("*.evalset_result.json"))
    Path(dest).write_bytes(new_file.read_bytes())


def run_baseline():
    _run_adk_eval_in_process("baseline_agent_app", "baseline.evalset_result.json")


def run_current():
    _run_adk_eval_in_process("current_agent_app", "current.evalset_result.json")
```

```bash
adk-tracegauge snapshot --entrypoint my_eval_suite:run_baseline --output baseline.json \
  --eval-history baseline.evalset_result.json
adk-tracegauge snapshot --entrypoint my_eval_suite:run_current --output current.json \
  --eval-history current.evalset_result.json
adk-tracegauge check --baseline baseline.json --current current.json
```

Note there is **no `--mode` flag above** — `check` defaults to `--mode auto`, which resolves
`eval_case_id` from the two `--eval-history` files and selects paired mode on its own. Real
output, from a genuine injected regression (32-case eval set, a fixed per-call prompt-token
bump added to the "current" agent variant — above the real default `--min-n=30`, a genuine
gate-passing verdict, not a demo that bypasses the real refusal floor), re-verified fresh
this session against a clean-built `adk-tracegauge` wheel installed into a fresh venv outside
any repo checkout, with `google-adk==2.7.0`:

```
adk-tracegauge check: mode=paired (key=eval_case_id, 32 overlapping eval_case_ids matched between baseline and current)
adk-tracegauge check [method=paired]: n_baseline=32 n_current=32 (min_n=30)
  mean_baseline=$0.005306  mean_current=$0.007106
  achieved power: minimum reliably-detectable effect at 80% power, given this run's observed variance/n, is ~$0.000000 (+0.00% of mean baseline) [normal approximation to the bootstrap CI -- see _regression.py module docstring for validated accuracy]
  observed effect: +0.001800 USD (+33.93%), 98% CI [+0.001800, +0.001800] (n_boot=10000, seed=42)
  statistically_significant=True practically_significant=True (floors: min_effect_usd=0.000100 OR min_effect_pct=5.00%)
  REGRESSION: cost increased significantly (CI excludes zero) AND the increase clears the configured practical-significance floor.
```
```
$ echo $?
1
```

**Measured detection rates for the shipped default (`--confidence 0.98`, `--min-n 30`),
stated honestly, not just "it works":** paired mode's false-positive rate is measured
*higher* than two-sample's at the same `n` (**1.40% [0.97%, 2.02%], 28/2,000 trials** vs.
**0.85% [0.53%, 1.36%], 17/2,000 trials**) — pairing buys detection power at a given `n`,
not a more reliable "clean" verdict. That power difference is large: paired mode detects a
true 10% cost regression **99.45% [99.02%, 99.69%] of the time (1,989/2,000 trials)** at
`n=30`, versus the two-sample fallback's **57.80% [55.62%, 59.95%] (1,156/2,000 trials)** on
the identical scenario — which is exactly why `--mode auto` prefers paired whenever it can.
The two-sample fallback remains real and live (no pairing key, insufficient overlap, or
`--mode two-sample` requested explicitly) and should not be assumed to inherit paired mode's
power. Both figures — Wilson 95% confidence intervals, 2,000 trials/cell — come from the
package's own `scripts/measure_regression_confidence_grid.py`; see its README ("Known
limitations" and "What this gate can and cannot detect") for the full 18+18-cell grid across
`confidence` ∈ {0.95, 0.98, 0.99} and `n` ∈ {30, 50}.

## Also: the `adk_tracegauge_cost_usd` metric inside `adk eval`

With the plugin wired in as shown above, register a threshold and `adk eval` itself prints
a real dollar score and PASSED/FAILED verdict per invocation:

```json
// test_config.json — the threshold this run must stay under, per invocation
{"criteria": {"adk_tracegauge_cost_usd": 0.05}}
```

```bash
adk eval assistant my_eval_set.json --config_file_path test_config.json --print_detailed_results
```

```
Overall Eval Status: PASSED
Metric: adk_tracegauge_cost_usd, Status: PASSED, Score: 0.0007999999999999999, Threshold: 0.05
```

(real output, verbatim — the float tail is genuine floating-point representation, not a typo)

**One real thing worth knowing before you rely on this path for anything CI-shaped:** `adk
eval`'s own *process exit code* does not reflect PASSED/FAILED — the real result lives in
`adk eval`'s stdout table and the persisted `.adk/eval_history/*.evalset_result.json` file,
not in `$?`. Use this path for inline visibility while iterating; use `adk-tracegauge check`
(above) for CI gating.

## Available metrics

| Metric | What it reports |
| ---- | ---- |
| `adk_tracegauge_cost_usd` | Dollar cost of one invocation, summed across every real model call within it (tool loops and sub-agent delegation can mean more than one model call per invocation). Raw USD in `score`; a real `PASSED`/`FAILED` verdict against a required max-USD-per-invocation threshold (`CostThresholdCriterion(threshold=...)`, or the deprecated `EvalMetric.threshold=`) — the evaluator raises `ValueError` at construction time if no threshold is set, rather than defaulting to a permissive always-PASSED sentinel. A per-call token/cost breakdown lives in the result's rationale. |

`CostThresholdCriterion` compares the opposite direction from ADK's built-in convention
(`PASSED` iff `cost <= threshold`, since cost is lower-is-better) — see [Known ADK-side
limitations](#known-adk-side-limitations) for the one place this inversion isn't honored
correctly by ADK itself.

Reports raw counts and dollars only — no calibrated efficiency bands, no trajectory-quality
judging. Pricing covers current-generation **Gemini**, **Claude**, and **GPT** models
(reached natively or through ADK's `LiteLlm` integration), plus **local/self-hosted**
models (Ollama, vLLM) — the latter require an explicit opt-in (`ADK_TRACEGAUGE_ASSUME_LOCAL`)
since a paid cloud product shares the same model-string prefix as local inference. An
invocation whose model isn't recognized reports `score=None` and `NOT_EVALUATED`, naming the
specific unresolved model — never a number computed from a fallback rate. See the project's
own README ("Pricing") for the full model list and the custom-price extension mechanism.

## Known ADK-side limitations

Two real, source-confirmed limitations in `google-adk` itself, independent of this package's
own correctness — worth knowing regardless of which path above you use:

- **`AgentEvaluator.evaluate()`'s pytest-style pass/fail is directionally unreliable for a
  lower-is-better metric like cost, at any threshold.** ADK's harness recomputes PASSED/FAILED
  itself from the deprecated legacy `threshold` scalar via `mean(scores) >= threshold` —
  hardcoded higher-is-better — instead of reading the metric's own, already-correct
  `eval_status`. `adk eval`/`LocalEvalService` are **unaffected** — they read `eval_status`
  directly and are always correct. Trust `adk eval`, `adk-tracegauge check`, or this metric's own
  `eval_status`; never `AgentEvaluator.evaluate()`'s assert/no-assert outcome for this
  specific metric. `adk-tracegauge` emits a real runtime warning when it detects this
  situation. A fix has been prepared and is pending submission upstream to `google/adk-python`.
- **`adk eval`'s own process exit code does not reflect PASSED/FAILED**, on any metric —
  the CLI prints a real pass/fail summary but the process always exits `0`. This is exactly
  why `adk-tracegauge check`, not `adk eval`, is the recommended CI-gating path above. A fix has
  been prepared and is pending submission upstream to `google/adk-python`.

Neither limitation is specific to `adk-tracegauge` — both apply to any custom metric
registered the same way. `adk-tracegauge check`'s own exit codes are unaffected by either, since
it never depends on `adk eval`'s own exit behavior.

## Resources

- [GitHub repository](https://github.com/gaurav-gandhi-2411/adk-tracegauge): source code,
  issues, and the full design rationale (including the measured statistical detection-power
  numbers behind `adk-tracegauge check`) in `README.md`.
- [PyPI package](https://pypi.org/project/adk-tracegauge/): releases and install
  instructions.
- [ADK Evaluation Guide](/evaluate/): background on ADK's evaluation framework and the
  `MetricEvaluatorRegistry` this package registers against.
