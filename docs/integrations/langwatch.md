---
catalog_title: LangWatch
catalog_description: Observability, tracing, evaluation, and prompt optimization for ADK agents
catalog_icon: /integrations/assets/langwatch.png
catalog_tags: ["observability", "evaluation"]
---

# LangWatch observability for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[LangWatch](https://langwatch.ai) is an open-source LLMOps platform for
observability, evaluation, and prompt optimization. It provides comprehensive
tracing for ADK agents using [OpenInference
instrumentation](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk),
allowing you to monitor, debug, and improve your agents in development and
production.

## Overview

LangWatch captures traces from ADK using its built-in OpenTelemetry support, giving you:

- **Automatic tracing** - Capture every agent run, tool call, and model request with full context
- **Online evaluation** - Continuously score production traffic for quality and safety
- **Guardrails** - Block or modify harmful responses in real-time
- **Prompt management** - Version, test, and optimize prompts with built-in A/B testing
- **Datasets and experiments** - Build evaluation sets from real traces and run batch experiments

## Installation

Install the required packages:

```bash
pip install langwatch openinference-instrumentation-google-adk google-adk
```

## Setup

Sign up at [langwatch.ai](https://langwatch.ai) or
[self-host](https://langwatch.ai/docs/self-hosting/overview) the platform, then
set your API key:

```bash
export LANGWATCH_API_KEY="your-langwatch-api-key"
export GOOGLE_API_KEY="your-gemini-api-key"
```

Initialize tracing:

```python
--8<-- "examples/inline/python/integrations/langwatch/001-setup.py"
```

That's it. All ADK agent activity will now be traced and sent to your LangWatch
dashboard automatically.

## Observe

With tracing initialized, run your ADK agent as usual and all interactions will
appear in LangWatch:

```python
--8<-- "examples/inline/python/integrations/langwatch/002-observe.py"
```

## Adding Custom Metadata

Use the `@langwatch.trace()` decorator to attach additional context to your
traces:

```python
--8<-- "examples/inline/python/integrations/langwatch/003-adding-custom-metadata.py"
```

## Support and Resources

- [LangWatch Documentation](https://langwatch.ai/docs)
- [ADK Integration Guide](https://langwatch.ai/docs/integration/python/integrations/google-ai)
- [LangWatch Repository on GitHub](https://github.com/langwatch/langwatch)
- [Community Discord](https://discord.gg/langwatch)
