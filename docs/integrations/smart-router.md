---
catalog_title: Smart Router Plugin
catalog_description: Prune large tool catalogs per session and log A/B routing with BigQuery Agent Analytics
catalog_icon: /integrations/assets/smart-router.svg
catalog_tags: ["observability", "evaluation", "resilience"]
---

# Smart Router plugin for ADK

<div class="language-support-tag"><span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span></div>

[Smart Router](https://github.com/statmike/adk-smart-router)
(`adk-smart-router`) is a runner-level plugin that reduces input token costs for
ADK agents with large tool catalogs (typically 25 to 100+ tools) while
preserving Gemini implicit context caching. On the first turn of each session,
the plugin selects a canonical menu of tools for the conversation and locks that
menu for all subsequent turns in the session so the prompt prefix remains
cache-eligible. It pairs directly with the
[BigQuery Agent Analytics plugin](/integrations/bigquery-agent-analytics/) for
zero-cold-start training from existing `agent_events` tables, live holdout A/B
evaluation, and automated BigQuery ML retraining, and includes a zero-shot
semantic judge (`PrototypeJudge`) that works on day zero before any traffic is
logged.

## Use cases

- **Prefix-preserving tool pruning**: Reduce a 25-to-100+ tool catalog to a
  smaller canonical tool menu on turn one and reuse that exact declaration
  prefix across the rest of the session so Gemini implicit context caching stays
  active.
- **Closed-loop routing with BigQuery Agent Analytics**: Stamp per-turn routing
  provenance (`decision_id`, `decision_source`, `kept_tools`, `confidence`, and
  `replica_id`) onto ADK events so the
  [BigQuery Agent Analytics plugin](/integrations/bigquery-agent-analytics/)
  persists them into `agent_events` for holdout A/B token comparisons and
  BigQuery ML retraining.
- **Day-zero semantic routing and hybrid new-tool rescue**: Route immediately
  with `PrototypeJudge` using `gemini-embedding-2` tool-schema embeddings and
  prerequisite-graph propagation, or combine trained `xgboost` routing with
  `PrototypeJudge` so newly added tools are scored before the next retrain.
- **Pre-provisioning prompt qualification**: Run `smart-router qualify` offline
  before provisioning cloud resources to verify whether pruning clears the
  model's context-cache floor or would fall into a cache-floor trap.
- **Principal-scoped tool result caching**: Cache deterministic read-only tool
  outputs in memory by `(principal, tool_name, canonical_args)` with automatic
  invalidation when mutating tools run.

## Pairing with BigQuery Agent Analytics

Smart Router does not create a separate logging pipeline or a second data
warehouse. Instead, it extends the `agent_events` table written by the
[BigQuery Agent Analytics plugin](/integrations/bigquery-agent-analytics/):

1. **Train from existing logs without waiting**: If your agent already logs to
   BigQuery through `BigQueryAgentAnalyticsPlugin`, you already have a training
   corpus. Run `smart-router readiness` against that dataset to verify whether
   your existing `agent_events` table has enough sessions and tool diversity to
   train a BigQuery ML boosted-tree router today.
2. **Capture per-turn routing provenance**: Register `SmartRouterPlugin` before
   `BigQueryAgentAnalyticsPlugin` on your `App` and include `"smart_router"` in
   `BigQueryLoggerConfig(custom_metadata_allowlist=["smart_router"])`. Smart
   Router stamps each turn's routing record onto `event.custom_metadata`, and
   `BigQueryAgentAnalyticsPlugin` writes it into
   `attributes.custom_metadata.smart_router` in `agent_events`.
3. **Measure savings against an unrouted holdout arm**: Smart Router keeps a
   configurable `holdout_fraction` (default `5%`) of sessions unrouted. Every
   reporting view and `smart-router status` query reads `agent_events` to
   compare billed input tokens, cache-hit rates, and tool-call recall between
   routed (`"fresh"`, `"reused"`) and unrouted (`"holdout"`) sessions within
   each replica.

## Prerequisites

- Python 3.11 or later.
- ADK Python (`google-adk>=1.22.0`), or `google-adk[bigquery-analytics]` when
  pairing with `BigQueryAgentAnalyticsPlugin`.
- A Google Cloud project with Gemini Enterprise enabled
  (`GOOGLE_GENAI_USE_ENTERPRISE=TRUE` and
  `gcloud auth application-default login`) for `gemini-embedding-2` prompt and
  tool embeddings when `mode="active"`.
- A BigQuery dataset and Cloud Storage bucket when using the
  [BigQuery Agent Analytics plugin](/integrations/bigquery-agent-analytics/) and
  trained `xgboost` model artifacts.

## Installation

```bash
pip install adk-smart-router
```

## Use with agent

Before enabling active routing, you can check offline whether your agent's
prompt size and tool catalog benefit from pruning:

```bash
smart-router qualify --app my_app.agent:app
```

If your agent already logs events with the
[BigQuery Agent Analytics plugin](/integrations/bigquery-agent-analytics/),
check whether your existing `agent_events` table is ready to train a model:

```bash
smart-router readiness --agent support_agent --project my-gcp-project --dataset my_bq_dataset
```

Attach `SmartRouterPlugin` to your `App` before `BigQueryAgentAnalyticsPlugin`
and allowlist `"smart_router"` in `BigQueryLoggerConfig` so routing decisions
and cache serves are recorded in BigQuery. By default, `RouterConfig` starts in
safe passthrough mode (`mode="off"`, `route_fraction=0.0`) until enabled by
configuration or environment variables.

```python
import asyncio

from adk_smart_router import RouterConfig, SmartRouterPlugin
from google.adk.agents import LlmAgent
from google.adk.agents.context_cache_config import ContextCacheConfig
from google.adk.apps import App
from google.adk.plugins.bigquery_agent_analytics_plugin import (
    BigQueryAgentAnalyticsPlugin,
    BigQueryLoggerConfig,
)
from google.adk.runners import InMemoryRunner
from google.genai import types


def get_order_status(order_id: str) -> dict[str, str]:
    """Look up the shipping status and carrier for an order ID."""
    return {"order_id": order_id, "status": "in_transit"}


def get_return_policy(category: str) -> dict[str, str]:
    """Return the refund and exchange policy window for a product category."""
    return {"category": category, "window_days": "30"}


root_agent = LlmAgent(
    name="support_agent",
    model="gemini-flash-latest",
    instruction="Resolve customer order and return questions using your tools.",
    tools=[get_order_status, get_return_policy],
)

router_plugin = SmartRouterPlugin(
    RouterConfig(
        bq_project="my-gcp-project",
        bq_dataset="my_bq_dataset",
        mode="active",
        route_fraction=1.0,
        judges=("prototype",),
        cacheable_tools={"get_return_policy": 3600},
    )
)

bigquery_analytics_plugin = BigQueryAgentAnalyticsPlugin(
    project_id="my-gcp-project",
    dataset_id="my_bq_dataset",
    config=BigQueryLoggerConfig(
        custom_metadata_allowlist=["smart_router"],
    ),
)

app = App(
    name="support_app",
    root_agent=root_agent,
    context_cache_config=ContextCacheConfig(min_tokens=2048, ttl_seconds=1800),
    plugins=[router_plugin, bigquery_analytics_plugin],
)


async def main() -> None:
    # Optional: pre-warm the embedder and tool-catalog prototypes before serving traffic.
    await router_plugin.warmup(app)

    runner = InMemoryRunner(app=app)
    session = await runner.session_service.create_session(
        user_id="user_1", app_name="support_app"
    )
    async for event in runner.run_async(
        user_id="user_1",
        session_id=session.id,
        new_message=types.Content(
            role="user",
            parts=[types.Part.from_text(text="Where is order ORD-100?")],
        ),
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text)


if __name__ == "__main__":
    asyncio.run(main())
```

Verify that your `App` registers `SmartRouterPlugin` before
`BigQueryAgentAnalyticsPlugin`, sets `ContextCacheConfig`, and includes
`"smart_router"` in `custom_metadata_allowlist`:

```bash
smart-router doctor --app my_app.agent:app
```

### Composable judge modes

The `judges` setting in `RouterConfig` (or `SMART_ROUTER_JUDGES`) selects how
the turn-one prompt embedding is scored against your tool catalog:

- **Cold-start (`judges=("prototype",)`):** Requires no historical logs and no
  Cloud Storage bucket. `PrototypeJudge` embeds each tool's docstring and
  parameter schema with `gemini-embedding-2`, subtracts the catalog mean vector,
  and propagates activation one hop upstream across `Returns:` to `Args:`
  prerequisite links.
- **Trained model (`judges=("xgboost",)`):** Loads the published BigQuery ML
  boosted-tree artifact (`model.ubj` and `metadata.json`) from Cloud Storage and
  maps top-K class probabilities to precomputed canonical tool menus.
- **Hybrid (`judges=("xgboost", "prototype")`):** Runs `xgboost` for tools known
  at training time and `PrototypeJudge` for newly deployed tools that are not
  yet in `metadata.json`, sharing a single turn-one prompt embedding across both
  judges.

## Available CLI commands

The `smart-router` CLI inspects agents offline and diagnoses live deployments:

| Command | Description |
| --- | --- |
| `smart-router qualify --app MODULE:ATTR` | Measures the agent's prompt and tool declarations offline and returns `PAYS`, `THIN`, `UNCACHED`, or `TRAP`, plus an argument-reachability graph audit. |
| `smart-router readiness --agent NAME --project ID` | Queries existing `BigQueryAgentAnalyticsPlugin` logs in `agent_events` to check whether an agent already has enough traffic and tool diversity to train a model. |
| `smart-router doctor --app MODULE:ATTR` | Checks plugin registration order relative to `BigQueryAgentAnalyticsPlugin`, `custom_metadata_allowlist`, `ContextCacheConfig`, and active judge configuration. |
| `smart-router check-arguments --app MODULE:ATTR --arguments FILE` | Audits held and supplied argument markings against logged first-turn user messages in BigQuery. |
| `smart-router status --agent NAME` | Reports the active model artifact, 7-day billed-token delta against the unrouted holdout arm in `agent_events`, feature drift, and retrain ledger status. |

## Configuration

Every field on `RouterConfig` can be passed in code or overridden at deploy time
through `load_config()` using environment variables:

| Parameter | Environment variable | Default | Description |
| --- | --- | --- | --- |
| `mode` | `SMART_ROUTER_MODE` | `"off"` | `"off"` (passthrough) or `"active"`. |
| `route_fraction` | `SMART_ROUTER_ROUTE_FRACTION` | `0.0` | Fraction of non-holdout sessions routed (`0.0` to `1.0`). |
| `holdout_fraction` | `SMART_ROUTER_HOLDOUT_FRACTION` | `0.05` | Permanent unrouted control arm used for A/B cost and quality comparison in BigQuery. |
| `judges` | `SMART_ROUTER_JUDGES` | `("xgboost",)` | Comma-separated judge tuple: `"prototype"`, `"xgboost"`, or `"xgboost,prototype"`. |
| `embedding_model` | `SMART_ROUTER_EMBEDDING_MODEL` | `"gemini-embedding-2"` | Gemini Enterprise embedding model ID (`SMART_ROUTER_EMBEDDING_DIMS` sets output dimension, default `768`). |
| `llm_judge_model` | `SMART_ROUTER_LLM_JUDGE_MODEL` | `"gemini-2.5-flash-lite"` | Gemini model ID used when `"llm_live"` is included in `judges`. |
| `bq_project` | `SMART_ROUTER_BQ_PROJECT` | `""` | Google Cloud project for Gemini Enterprise embeddings and BigQuery tables. |
| `bq_dataset` | `SMART_ROUTER_BQ_DATASET` | `"smart_router"` | BigQuery dataset containing `BigQueryAgentAnalyticsPlugin` events and router metadata tables. |
| `gcs_bucket` | `SMART_ROUTER_GCS_BUCKET` | `""` | Cloud Storage bucket storing published `xgboost` model artifacts. |
| `never_prune` | (code only) | `frozenset()` | Tool names that are never pruned on any routed session. |
| `prunable_by_default` | (code only) | `frozenset()` | Unseen or classless tool names eligible to be pruned when not predicted. |
| `cacheable_tools` | (code only) | `{}` | Mapping of read-only tool names to TTL in seconds for principal-scoped result caching (non-listed tools automatically purge the principal's cache on write). |

## Additional resources

- [BigQuery Agent Analytics plugin](/integrations/bigquery-agent-analytics/)
- [Smart Router GitHub](https://github.com/statmike/adk-smart-router)
- [adk-smart-router on PyPI](https://pypi.org/project/adk-smart-router/)
