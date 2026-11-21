---
catalog_title: Agnost AI
catalog_description: Monitor production agent conversations, users, and tool calls
catalog_icon: /integrations/assets/agnost.png
catalog_tags: ["observability", "evaluation"]
---

# Agnost AI observability for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Agnost AI](https://agnost.ai) monitors AI agents in production. It reads the
OpenTelemetry spans ADK emits and groups them into conversations and users, then
runs online evals on finished conversations and can alert in Slack. ADK's
built-in OTLP export sends the spans, so no extra instrumentation library is
needed.

## Overview

- **Conversations**: Each ADK session becomes one conversation, keyed on the
  `gen_ai.conversation.id` attribute ADK writes on its spans.
- **Users**: The session's `user_id`, added to the root span by a small plugin.
- **Transcripts**: The user message and final answer of each turn.
- **Events**: Agent, model, and tool spans in a nested tree, with model names,
  token counts, and tool arguments and results.

## Prerequisites

- An Agnost AI account. Sign in at [app.agnost.ai](https://app.agnost.ai) and
  copy your **Organization ID** from **Settings** > **General**.
- A Gemini API key set as `GOOGLE_API_KEY`.

## Installation

```bash
pip install google-adk opentelemetry-exporter-otlp-proto-http
```

ADK's OTLP setup uses the HTTP/protobuf exporter. Without this package, ADK
logs a warning and exports nothing.

## Setup

Set these environment variables before ADK starts:

```bash
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT="https://otel.agnost.ai/v1/traces"
export OTEL_EXPORTER_OTLP_TRACES_HEADERS="X-Agnost-Org-ID=YOUR_ORG_ID"
export OTEL_SERVICE_NAME="weather-agent"
export OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT="SPAN_ONLY"
```

The trace-specific variables send only traces, which is all Agnost AI stores.
Setting `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` to `SPAN_ONLY`
puts prompts, answers, and tool arguments on the spans. Without it, Agnost AI
receives model and tool events with no content.

With these variables set, `adk web` and `adk api_server` export traces to
Agnost AI. In your own process, call `maybe_set_otel_providers()` once at
startup.

## Observe

ADK records `user.id` on log records rather than spans, and its root
`invoke_workflow` span carries no message content. The `AgnostPlugin` below
copies the user ID, the user's message, and the final answer onto that root
span. It only sets span attributes and does not change how the agent runs.

```python
import asyncio
import json

from google.adk.agents import Agent
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.telemetry.setup import maybe_set_otel_providers
from google.genai import types
from opentelemetry import trace

maybe_set_otel_providers()


def _text(content):
    return "".join(p.text for p in (content.parts or []) if p.text) if content else ""


class AgnostPlugin(BasePlugin):
    """Adds user.id and each turn's input and answer to ADK's root span."""

    def __init__(self):
        super().__init__(name="agnost")

    async def on_user_message_callback(self, *, invocation_context, user_message):
        span = trace.get_current_span()  # the root invoke_workflow span
        span.set_attribute("user.id", invocation_context.session.user_id)
        span.set_attribute("gen_ai.input.messages", json.dumps(
            [{"role": "user", "parts": [{"type": "text", "content": _text(user_message)}]}]))

    async def on_event_callback(self, *, invocation_context, event):
        if event.is_final_response() and _text(event.content):
            trace.get_current_span().set_attribute("gen_ai.output.messages", json.dumps(
                [{"role": "assistant", "parts": [{"type": "text", "content": _text(event.content)}]}]))


def get_weather(city: str) -> dict:
    """Returns the current weather for a city."""
    return {"status": "success", "report": f"The weather in {city} is sunny."}


root_agent = Agent(
    name="weather_agent",
    model="gemini-flash-latest",
    instruction="Answer weather questions using get_weather.",
    tools=[get_weather],
)


async def main():
    sessions = InMemorySessionService()
    await sessions.create_session(
        app_name="weather_app", user_id="user-42", session_id="session-abc"
    )
    runner = Runner(
        agent=root_agent,
        app_name="weather_app",
        session_service=sessions,
        plugins=[AgnostPlugin()],
    )
    async for event in runner.run_async(
        user_id="user-42",
        session_id="session-abc",
        new_message=types.Content(
            role="user", parts=[types.Part(text="What's the weather in Paris?")]
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(event.content.parts[0].text)

    # ADK exports spans in batches; flush before a short script exits.
    trace.get_tracer_provider().force_flush()


asyncio.run(main())
```

When you serve an `App` with `adk web`, pass the plugin as
`App(plugins=[AgnostPlugin()])` instead.

Open **Conversations** in Agnost AI after a minute or two. Every `run_async`
call with the same `session_id` lands in the same conversation, attributed to
`user-42`, with the user message, the answer, and a `get_weather` tool event.

If your app sets its own `TracerProvider` before ADK starts, ADK leaves it in
place. Add an `OTLPSpanExporter` for `https://otel.agnost.ai/v1/traces` with the
`X-Agnost-Org-ID` header to that provider instead.

## Support and Resources

- [Agnost AI ADK guide](https://docs.agnost.ai/google-adk)
- [Agnost AI documentation](https://docs.agnost.ai)
- [ADK traces](/observability/traces/)
- [ADK plugins](/plugins/)
