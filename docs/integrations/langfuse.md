---
catalog_title: Langfuse
catalog_description: Open-source AI engineering platform to debug, analyze, and iterate on LLM applications
catalog_icon: /integrations/assets/langfuse.png
catalog_tags: ["observability", "evaluation"]
---

# Langfuse observability for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Langfuse](https://langfuse.com) is an open-source LLM engineering platform for observability, evaluation, and prompt management. It captures detailed traces from ADK agents using the OpenTelemetry (OTel) protocol, so you can debug, evaluate, and iterate on agent apps in development and production.

## Overview

Langfuse captures traces from ADK using OpenTelemetry and supports the
[AI Engineering Loop](https://langfuse.com/academy/ai-engineering-loop):

- **[Trace](https://langfuse.com/academy/tracing)**: Capture the full path of a
request, including prompts, retrieved context, tool calls, outputs, latency,
and cost
- **[Monitor](https://langfuse.com/academy/monitoring)**: Track how the system
behaves over time and surface the traces that deserve attention, using
evaluation methods, user feedback, and cost or latency anomalies
- **[Build datasets](https://langfuse.com/academy/datasets)**: Turn real
scenarios from monitoring and expected scenarios from development into
repeatable test cases
- **[Experiment](https://langfuse.com/academy/experiments)**: Change variables
systematically (a prompt, a model, a retrieval strategy) and compare each
change against a stable baseline
- **[Evaluate](https://langfuse.com/academy/evaluate)**: Decide whether results
are good enough to ship using manual review, code evaluator checks, or
LLM-as-a-judge

## Installation

Install the required packages:

```bash
pip install langfuse "google-adk>=2" openinference-instrumentation-google-adk
```

`google-adk` 2.x requires Python 3.10 or later. Pinning `"google-adk>=2"` ensures
pip installs the current ADK 2.x release.

## Setup

Sign up at [cloud.langfuse.com](https://cloud.langfuse.com) or
[self-host](https://langfuse.com/self-hosting) the platform, then set your API
keys. Get keys from your project settings page. Also set a
[Gemini API key](https://aistudio.google.com/app/apikey):

```bash
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."
export LANGFUSE_BASE_URL="https://cloud.langfuse.com"  # EU region
# Other regions: https://us.cloud.langfuse.com (US),
# https://jp.cloud.langfuse.com (Japan), https://hipaa.cloud.langfuse.com (HIPAA)
export GOOGLE_API_KEY="your-gemini-api-key"
```

Initialize the Langfuse client and instrument ADK:

```python
--8<-- "examples/inline/python/integrations/langfuse/001-https-jp-cloud-langfuse-com-japan-https.py"
```

That's it. All ADK agent activity will now be traced and sent to your Langfuse
project automatically.

## Observe

With tracing initialized, run your ADK agent as usual and all interactions will
appear in Langfuse:

```python
--8<-- "examples/inline/python/integrations/langfuse/002-observe.py"
```

Langfuse automatically maps the `user_id` and `session_id` you pass to
`runner.run()` to the trace's **user** and **session** — you get
[user](https://langfuse.com/docs/observability/features/users) and
[session](https://langfuse.com/docs/observability/features/sessions) tracking
without any extra code.

## Named and filterable traces

By default, traces are named after the ADK app. Use
[`propagate_attributes`](https://langfuse.com/docs/observability/sdk/instrumentation)
to set a descriptive trace name, tags, and metadata so you can filter traces in
Langfuse.

Use the async `runner.run_async()` API when setting attributes this way. The
synchronous `runner.run()` executes the agent on a background worker thread, so
OpenTelemetry context (and attributes from `propagate_attributes`) does not
reach the ADK spans:

```python
--8<-- "examples/inline/python/integrations/langfuse/003-named-and-filterable-traces.py"
```

## View traces in Langfuse

Open your **Langfuse dashboard → Traces** to inspect agent loops, tool calls,
and model generations. Traces are filterable by the users, sessions, and tags
set above.

![Google ADK example trace in Langfuse](https://langfuse.com/images/cookbook/integration-google-adk/google-adk-trace.png)

For multi-agent pipelines, scoring traces with user feedback, and more examples,
see the [Langfuse ADK integration
guide](https://langfuse.com/integrations/frameworks/google-adk).

## Support and Resources

- [Langfuse Documentation](https://langfuse.com/docs)
- [ADK Integration Guide](https://langfuse.com/integrations/frameworks/google-adk)
- [Langfuse Repository on GitHub](https://github.com/langfuse/langfuse)

