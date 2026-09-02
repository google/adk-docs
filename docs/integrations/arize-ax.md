---
catalog_title: Arize AX
catalog_description: Production-grade observability, debugging, and improvement of LLM applications
catalog_icon: /integrations/assets/arize.png
catalog_tags: ["observability", "evaluation"]
---

# Arize AX observability for ADK

[Arize AX](https://arize.com/docs/ax) is a production-grade observability platform for monitoring, debugging, and improving LLM applications and AI Agents at scale. It provides comprehensive tracing, evaluation, and monitoring capabilities for your Google ADK applications. To get started, sign up for a [free account](https://app.arize.com/auth/join).

For an open-source, self-hosted alternative, check out [Phoenix](https://arize.com/docs/phoenix).

## Overview

Arize AX can automatically collect traces from Google ADK using [OpenInference instrumentation](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk), allowing you to:

- **Trace agent interactions** - Automatically capture every agent run, tool call, model request, and response with context and metadata
- **Evaluate performance** - Assess agent behavior using custom or pre-built evaluators and run experiments to test agent configurations
- **Monitor in production** - Set up real-time dashboards and alerts to track performance
- **Debug issues** - Analyze detailed traces to quickly identify bottlenecks, failed tool calls, and any unexpected agent behavior

![Agent Traces](https://storage.googleapis.com/arize-phoenix-assets/assets/images/google-adk-traces.png)

## Installation

Install the required packages:

```bash
pip install openinference-instrumentation-google-adk google-adk arize-otel
```

## Setup

### 1. Configure Environment Variables { #configure-environment-variables }

Set your Google API key:

```bash
export GOOGLE_API_KEY=[your_key_here]
```

### 2. Connect your application to Arize AX { #connect-your-application-to-arize-ax }

```python
--8<-- "examples/inline/python/integrations/arize-ax/001-2-connect-your-application-to-arize-ax-c.py"
```

## Observe

Now that you have tracing setup, all Google ADK SDK requests will be streamed to Arize AX for observability and evaluation.

```python
--8<-- "examples/inline/python/integrations/arize-ax/002-observe.py"
```
## View Results in Arize AX
![Traces in Arize AX](https://storage.googleapis.com/arize-phoenix-assets/assets/images/google-adk-dashboard.png)
![Agent Visualization](https://storage.googleapis.com/arize-phoenix-assets/assets/images/google-adk-agent.png)
![Agent Experiments](https://storage.googleapis.com/arize-phoenix-assets/assets/images/google-adk-experiments.png)

## Support and Resources
- [Arize AX Documentation](https://arize.com/docs/ax/integrations/python-agent-frameworks/google-adk)
- [Arize Community Slack](https://arize-ai.slack.com/join/shared_invite/zt-11t1vbu4x-xkBIHmOREQnYnYDH1GDfCg#/shared-invite/email)
- [OpenInference Package](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk)
