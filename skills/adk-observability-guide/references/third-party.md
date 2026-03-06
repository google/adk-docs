# Third-Party Observability Integrations

> Third-party integrations can be added to any ADK project, scaffolded or not.

All integrations capture agent execution traces, LLM calls, and tool use. Choose based on your team's needs.

---

## AgentOps

**When to use:** Quick setup with session replay visualization. Good for debugging agent flows and tracking LLM cost/latency.

**Key details:**
- 2-line setup — `pip install agentops` + `agentops.init()`
- Replaces ADK's native telemetry with its own span hierarchy
- SaaS only (requires API key from agentops.ai)

**ADK docs:** `WebFetch: https://google.github.io/adk-docs/integrations/agentops/index.md`

---

## Phoenix (Arize)

**When to use:** Open-source observability with custom evaluators and experiment testing. Good for teams wanting self-hosted or full control.

**Key details:**
- Uses OpenInference instrumentation (not OTel directly)
- Supports custom evaluators for performance scoring
- Available as cloud service or self-hosted

**ADK docs:** `WebFetch: https://google.github.io/adk-docs/integrations/phoenix/index.md`

---

## MLflow

**When to use:** Teams already using MLflow for ML experiment tracking. Ingests OTel traces into MLflow Tracking Server.

**Key details:**
- Requires MLflow 3.6.0+ with SQL backend store (SQLite, PostgreSQL, MySQL)
- Uses OTLP exporter to send ADK spans to MLflow
- Span tree visualization for debugging

**ADK docs:** `WebFetch: https://google.github.io/adk-docs/integrations/mlflow/index.md`

---

## Monocle

**When to use:** Minimal setup with local-first tracing. Good for individual developers who want VS Code visualization.

**Key details:**
- 1-call setup — `setup_monocle_telemetry(workflow_name="...")`
- Exports OTel-compatible traces to local files or console
- VS Code extension (Okahu Trace Visualizer) for interactive Gantt charts

**ADK docs:** `WebFetch: https://google.github.io/adk-docs/integrations/monocle/index.md`

---

## W&B Weave

**When to use:** Teams on the Weights & Biases platform wanting unified agent observability with team collaboration features.

**Key details:**
- Timeline views of agent calls and trace hierarchies
- Requires `WANDB_API_KEY` environment variable
- Uses OTLP exporter configuration

**ADK docs:** `WebFetch: https://google.github.io/adk-docs/integrations/weave/index.md`

---

## Freeplay

**When to use:** Teams wanting observability + prompt management + evaluation in one platform. Good for prompt iteration workflows.

**Key details:**
- Observability focused on agents, LLM calls, and tool use
- Online/offline evaluation with automated scorers
- Prompt management with version control and direct code updates
- `FreeplayLLMAgent` for version-controlled prompts and batch testing

**ADK docs:** `WebFetch: https://google.github.io/adk-docs/integrations/freeplay/index.md`
