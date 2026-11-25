---
catalog_title: Confident AI
catalog_description: OpenTelemetry-native tracing and evaluation for ADK agents
catalog_icon: /integrations/assets/confident-ai.png
catalog_tags: ["observability", "evaluation"]
---

# Confident AI observability for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Confident AI](https://www.confident-ai.com/) is an LLM observability and
evaluation platform for teams building reliable AI applications in development
and production. It captures traces from ADK agents with
[`confident-trace`](https://github.com/confident-ai/confident-trace), its
OpenTelemetry-native tracing SDK, so you can debug agent runs and score them
against evaluation metrics.

## Overview

ADK already emits its own OpenTelemetry spans for invocations, agents, model
calls, and tools. `confident-trace` picks those spans up and exports them to
Confident AI without wrapping the framework, so there is no instrumentor to
register and no change to how you build agents.

Once traces arrive, Confident AI supports:

- **[Tracing](https://www.confident-ai.com/docs/llm-tracing/introduction)**:
Inspect each invocation as a trace with its full agent, model, and tool
hierarchy
- **[Token usage and cost](https://www.confident-ai.com/docs/llm-tracing/features/token-usage-cost)**:
See what each model call spent, rolled up per trace
- **[Online evals](https://www.confident-ai.com/docs/llm-tracing/online-evals)**:
Score traces automatically as they are ingested, using metric collections
defined in your project
- **[Threads](https://www.confident-ai.com/docs/llm-tracing/features/threads)**:
Group an agent's turns into one conversation you can view and evaluate as a
unit

## Installation

Install the required packages:

```bash
pip install confident-trace google-adk
```

The `confident-trace` package requires Python 3.10 or later.

## Setup

Get your project API key from [Confident AI](https://app.confident-ai.com),
then set it along with a
[Gemini API key](https://aistudio.google.com/app/apikey):

```bash
export CONFIDENT_API_KEY="<your-confident-api-key>"
export GOOGLE_API_KEY="<your-google-key>"
```

For users in the EU region, set the OTEL endpoint to the EU version:

```bash
export CONFIDENT_OTEL_ENDPOINT="https://eu.otel.confident-ai.com/v1/traces"
```

Call `init()` once at startup, before your runner runs:

```python
from confident_trace import init

init()
```

That's it. All ADK agent activity is now traced and sent to your Confident AI
project automatically.

## Observe

With tracing initialized, run your ADK agent as usual and all interactions
appear in Confident AI:

```python
import asyncio

from confident_trace import init, shutdown
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types


async def main():
    init()
    agent = Agent(
        name="my_agent",
        model="gemini-flash-latest",
        description="A helpful assistant.",
        instruction="Answer questions concisely.",
    )
    runner = InMemoryRunner(app_name="my_app", agent=agent)
    session = await runner.session_service.create_session(
        app_name="my_app", user_id="user-42"
    )
    try:
        async for event in runner.run_async(
            user_id="user-42",
            session_id=session.id,
            new_message=types.Content(
                role="user", parts=[types.Part(text="What is OpenTelemetry?")]
            ),
        ):
            if event.content and event.content.parts:
                print(event.content.parts[0].text or "", end="")
        print()
    finally:
        shutdown()


asyncio.run(main())
```

Your ADK code stays exactly the same. `confident-trace` automatically attaches a
`Google ADK` integration label to your spans and captures:

- **Invocation lifecycle**: Operation names, timing, status, and session
context for each run.
- **Agent execution**: Which agents participated and the order in which they
ran.
- **Model calls**: Request and response content, model details, finish
reasons, and
[token usage](https://www.confident-ai.com/docs/llm-tracing/features/token-usage-cost).
- **Tool calls**: Tool names and their
[input/output](https://www.confident-ai.com/docs/llm-tracing/features/input-output).
- **Errors**: Failed operations retain their error status in the trace.

ADK puts some message content into OpenTelemetry *logs* rather than spans.
The `confident-trace` SDK exports traces only, so if content looks thinner than you
expect, check that `ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS` isn't set to `false`.
That variable, and ADK's own telemetry configuration, controls what ADK puts on
its spans.

In a long-running server, call `init()` at startup and `shutdown()` during
graceful shutdown, after active invocations finish. Do not call them per
request.

If you don't see a trace, it is almost always because the program exited before
the traces were posted. Make sure you're calling `shutdown()` (or `flush()` in
long-running processes) before exit.

## Online evals

You can configure what happens to your incoming traces on Confident AI's [workflows page](https://www.confident-ai.com/docs/llm-tracing/workflows).

![Confident AI workflows page](https://confident-docs.s3.us-east-1.amazonaws.com/confident-trace-workflows.png)

Here are the workflows you can configure:

- **Evaluation rules**: Evaluate incoming traces against a [metric collection](https://www.confident-ai.com/docs/metrics/metric-collections).
- **Classifiers**: Label your traces by issue, sentiment, or any dimension you define, which lets you group or filter them later on.
- **Queue ingestion**: Route your production traces into annotation queues for your internal review team to annotate them by hand.
- **Dataset ingestion**: Ingest your production traces into datasets to reuse as test cases and iterate on results to improve over time.

You can create custom workflows for different data models like traces, spans, and threads individually as per your needs.

To evaluate a component or trace manually, pass a metric collection via `update_trace`. See [online evaluations](https://www.confident-ai.com/docs/llm-tracing/online-evals).

## Trace properties

Use a trace context to attach tags, metadata, and a user ID that you know
before the invocation starts. It creates no extra span. The trace started by
`runner.run_async()` inherits everything you pass:

```python
from confident_trace import init, trace_context
from google.genai import types

init()

message = types.Content(role="user", parts=[types.Part(text="Explain OpenTelemetry.")])

async with trace_context(
    tags=["support"],
    metadata={"release": "2026-09"},
    user_id="user-42",
):
    async for event in runner.run_async(
        user_id="user-42", session_id=session.id, new_message=message
    ):
        pass
```

## Group traces into threads

The `confident-trace` SDK provides a `turn()` method you can use to group two sequential
invocations into one turn. Reuse the same thread ID on later turns to group
them into one thread you can view and evaluate on Confident AI:

```python
from confident_trace import init, turn
from google.genai import types

init()

with turn("support-turn", thread_id="chat-42"):
    async for event in runner.run_async(
        user_id="user-42",
        session_id=session.id,
        new_message=types.Content(
            role="user", parts=[types.Part(text="Find the relevant account details.")]
        ),
    ):
        pass
```

## Existing OpenTelemetry providers

ADK writes its spans to the shared **global** OpenTelemetry tracer provider,
and that's where `init()` installs the Confident AI exporter. If your app
configures its own provider, register that same provider as the global one
before ADK initializes. See
[existing OpenTelemetry provider](https://www.confident-ai.com/docs/integrations/opentelemetry#existing-opentelemetry-provider).

Calling `google-genai` directly outside ADK, or inside a tool function? Those
calls are traced by the Google GenAI provider integration and show up as
[LLM spans](https://www.confident-ai.com/docs/llm-tracing/features/span-types#llm-spans).
Calls made through ADK are only recorded once, on ADK's own model span, so you
never see duplicates.

## Support and Resources

- [ADK integration guide](https://www.confident-ai.com/docs/integrations/third-party/google-adk)
- [LLM tracing on Confident AI](https://www.confident-ai.com/docs/llm-tracing/introduction)
- [Online evals](https://www.confident-ai.com/docs/llm-tracing/online-evals)
- [confident-trace on GitHub](https://github.com/confident-ai/confident-trace)
- **Need help integrating?** [Talk to a human.](https://www.confident-ai.com/book-a-demo)
