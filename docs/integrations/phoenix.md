---
catalog_title: Phoenix
catalog_description: Open-source, self-hosted observability, tracing, and evaluation of LLM applications
catalog_icon: /integrations/assets/phoenix.png
catalog_tags: ["observability", "evaluation"]
---

# Phoenix observability for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Phoenix](https://arize.com/docs/phoenix) is an open-source, self-hosted observability platform for monitoring, debugging, and improving LLM applications and AI Agents at scale. It provides comprehensive tracing and evaluation capabilities for your Google ADK applications. To get started, sign up for a [free account](https://arize.com/phoenix/).


## Overview

Phoenix can automatically collect traces from Google ADK using [OpenInference instrumentation](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk), allowing you to:

- **Trace agent interactions** - Automatically capture every agent run, tool call, model request, and response with full context and metadata
- **Evaluate performance** - Assess agent behavior using custom or pre-built evaluators and run experiments to test agent configurations
- **Debug issues** - Analyze detailed traces to quickly identify bottlenecks, failed tool calls, and unexpected agent behavior
- **Self-hosted control** - Keep your data on your own infrastructure

## Installation

### 1. Install Required Packages { #install-required-packages }

```bash
pip install openinference-instrumentation-google-adk google-adk arize-phoenix-otel
```

## Setup

### 1. Launch Phoenix { #launch-phoenix }

These instructions show you how to use Phoenix Cloud. You can also [launch Phoenix](https://arize.com/docs/phoenix/integrations/llm-providers/google-gen-ai/google-adk-tracing) in a notebook, from your terminal, or self-host it using a container.

1. Sign up for a [free Phoenix account](https://arize.com/phoenix/).
2. From the Settings page of your new Phoenix Space, create your API key
3. Copy your endpoint which should look like: https://app.phoenix.arize.com/s/[your-space-name]

**Set your Phoenix endpoint and API Key:**

```python
--8<-- "examples/inline/python/integrations/phoenix/001-1-launch-phoenix-launch-phoenix.py"
```

### 2.  Connect your application to Phoenix { #connect-your-application-to-phoenix }

```python
--8<-- "examples/inline/python/integrations/phoenix/002-2-connect-your-application-to-phoenix-co.py"
```

## Observe

Now that you have tracing setup, all Google ADK SDK requests will be streamed to Phoenix for observability and evaluation.

```python
--8<-- "examples/inline/python/integrations/phoenix/003-observe.py"
```

## Support and Resources
- [Phoenix Documentation](https://arize.com/docs/phoenix/integrations/llm-providers/google-gen-ai/google-adk-tracing)
- [Community Slack](https://arize-ai.slack.com/join/shared_invite/zt-11t1vbu4x-xkBIHmOREQnYnYDH1GDfCg#/shared-invite/email)
- [OpenInference Package](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk)
