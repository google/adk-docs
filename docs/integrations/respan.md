---
catalog_title: Respan
catalog_description: Trace, debug, and monitor ADK agents with Respan observability
catalog_icon: /integrations/assets/respan.svg
catalog_tags: ["observability"]
---

# Respan observability for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Respan](https://www.respan.ai/) captures ADK runner, agent, model, and tool
spans so you can inspect complete agent workflows in the Respan platform. The
ADK integration uses
[`respan-instrumentation-google-adk`](https://pypi.org/project/respan-instrumentation-google-adk/),
which wraps the OpenInference ADK instrumentor and adds Respan-specific span
normalization before traces are exported.

## Overview

Use Respan with ADK to:

- **Trace agent runs**: Capture runner invocations, agent execution, model calls,
  and tool calls in one trace.
- **Debug failures**: Inspect span inputs, outputs, timing, and errors across
  nested ADK workflows.
- **Track production metadata**: Attach customer, thread, environment, and custom
  metadata to all spans from a request.
- **Route models through the Respan gateway**: Use ADK's LiteLLM adapter with
  Respan's OpenAI-compatible gateway when you want centralized model routing.

## Prerequisites

- Python 3.11, 3.12, or 3.13.
- A [Respan API key](https://platform.respan.ai/platform/api/api-keys).
- A Google API key if your ADK agent calls Gemini directly.

## Installation

Install the Respan SDK, the ADK instrumentor, and ADK:

```bash
pip install respan-ai respan-instrumentation-google-adk "google-adk[extensions]"
```

Set the required environment variables:

```bash
export RESPAN_API_KEY="YOUR_RESPAN_API_KEY"
export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
```

`RESPAN_API_KEY` sends traces to Respan. `GOOGLE_API_KEY` is used by direct
Gemini model calls.

## Trace an ADK agent

Initialize Respan before running the ADK agent. All ADK runs started after
initialization are traced automatically.

```python
--8<-- "examples/inline/python/integrations/respan/001-trace-an-adk-agent.py"
```

Open the [Respan traces page](https://platform.respan.ai/platform/traces) to see
the ADK workflow with runner, agent, model, and tool spans.

## Add request metadata

Use `propagate_attributes()` to add per-request identifiers and metadata to all
spans produced inside the context.

```python
--8<-- "examples/inline/python/integrations/respan/002-add-request-metadata.py"
```

## Trace tool calls

ADK tools are captured as child tool spans with serialized inputs, outputs, and
timing.

```python
--8<-- "examples/inline/python/integrations/respan/003-trace-tool-calls.py"
```

## Use the Respan gateway

ADK can route model calls through the Respan gateway with its LiteLLM adapter.
This is useful when you want one OpenAI-compatible endpoint for multiple model
providers.

```bash
export RESPAN_API_KEY="YOUR_RESPAN_API_KEY"
export RESPAN_BASE_URL="https://api.respan.ai/api"
export RESPAN_MODEL="openai/gpt-5-mini"
```

```python
--8<-- "examples/inline/python/integrations/respan/004-use-the-respan-gateway.py"
```

## Resources

- [Respan ADK tracing docs](https://www.respan.ai/docs/integrations/google-adk)
- [Respan ADK gateway docs](https://www.respan.ai/docs/integrations/gateway/google-adk)
- [Respan Python examples](https://github.com/respanai/respan-example-projects/tree/main/python/tracing/google-adk)
- [Respan platform](https://platform.respan.ai/platform/traces)
