---
catalog_title: Dash0
catalog_description: Trace agents with OpenTelemetry and query telemetry over MCP
catalog_icon: /integrations/assets/dash0.png
catalog_tags: ["observability", "mcp"]
---

# Dash0 observability for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Dash0](https://www.dash0.com) is an OpenTelemetry-native observability
platform for traces, metrics, and logs. ADK already emits OpenTelemetry data
that follows the [GenAI semantic
conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/), so you can
send it to Dash0 with environment variables alone. Dash0 also runs a hosted MCP
server, which lets an ADK agent query the same telemetry.

## Overview

- **Agent traces**: Each run shows up as an `invoke_agent` span with child spans
  for model calls and tool executions, next to the traces of the services your
  tools call.
- **Token usage and cost**: Dash0 reads the GenAI attributes on model spans and
  derives token usage and cost metrics from them.
- **Evaluations**: Dash0 [evals](https://www.dash0.com/docs/dash0/ai/observability/evals)
  score recorded conversations once message content is on the spans.
- **Telemetry tools for agents**: The [Dash0 MCP
  server](https://www.dash0.com/docs/dash0/ai/mcp) gives an agent read-only
  tools for services, metrics, logs, traces, and failed checks.

## Prerequisites

- A [Dash0 account](https://www.dash0.com)
- An [auth token](https://www.dash0.com/docs/dash0/miscellaneous/glossary/auth-tokens)
  with ingest permission to send telemetry, and one with read permission to use
  the MCP server
- Your organization's OTLP via HTTP
  [endpoint](https://www.dash0.com/docs/dash0/miscellaneous/glossary/endpoints),
  such as `https://ingress.eu-west-1.aws.dash0.com`, from **Settings →
  Endpoints** in Dash0

## Installation

```bash
pip install "google-adk[otel]"
```

The `otel` extra installs the OTLP HTTP exporter that ADK uses.

## Setup

Set the standard OpenTelemetry environment variables:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT="https://ingress.eu-west-1.aws.dash0.com"
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer%20YOUR_DASH0_AUTH_TOKEN"
export OTEL_SERVICE_NAME="weather-agent"
```

Use the endpoint shown for your organization and leave the path off. ADK
exports traces, metrics, and logs, and the exporter appends `/v1/traces`,
`/v1/metrics`, and `/v1/logs`. The `%20` encodes the space after `Bearer`.

Dash0 writes to the token's default
[dataset](https://www.dash0.com/docs/dash0/miscellaneous/glossary/datasets). To
pick another one, add a `Dash0-Dataset` header:

```bash
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer%20YOUR_DASH0_AUTH_TOKEN,Dash0-Dataset=my-dataset"
```

With these variables set, `adk web` and `adk api_server` export to Dash0 with
no code changes.

### Capture prompts and responses

By default, ADK does not write `gen_ai.input.messages` and
`gen_ai.output.messages` onto its GenAI spans. Dash0 evals judge the
conversation on the span, so set the content capture mode to `SPAN_ONLY` if you
want to evaluate it:

```bash
export OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT="SPAN_ONLY"
```

To evaluate content without storing it, turn on GenAI attribute redaction for
the dataset in Dash0. Evals run before redaction, so they still judge the
original text.

## Observe

When you run the agent from your own code, call `maybe_set_otel_providers()`
once at startup. It reads the environment variables above and sets up the
exporters.

```python
import asyncio

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.telemetry.setup import maybe_set_otel_providers
from google.genai import types

maybe_set_otel_providers()


def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": "The weather in New York is sunny with a temperature of 25 degrees Celsius.",
        }
    return {
        "status": "error",
        "error_message": f"Weather information for '{city}' is not available.",
    }


root_agent = Agent(
    name="weather_agent",
    model="gemini-flash-latest",
    description="Agent to answer questions using weather tools.",
    instruction="You must use the available tools to find an answer.",
    tools=[get_weather],
)


async def main():
    runner = InMemoryRunner(agent=root_agent, app_name="weather_app")
    session = await runner.session_service.create_session(
        app_name="weather_app", user_id="test_user"
    )
    async for event in runner.run_async(
        user_id="test_user",
        session_id=session.id,
        new_message=types.Content(
            role="user", parts=[types.Part(text="What is the weather in New York?")]
        ),
    ):
        if event.is_final_response():
            print(event.content.parts[0].text.strip())


asyncio.run(main())
```

Open **Tracing** in Dash0 and filter by the `weather-agent` service. The
**Gen AI** tab in the span sidebar shows the model, parameters, token usage,
and response for each model call. See [About GenAI
Spans](https://www.dash0.com/docs/dash0/telemetry/tracing/about-gen-ai-spans)
for the attributes Dash0 reads.

## Query Dash0 from an agent

The Dash0 MCP server is hosted and uses the streamable HTTP transport. Each
region has its own endpoint, such as `https://api.eu-west-1.aws.dash0.com/mcp`.
Copy yours from **Settings → Endpoints** under **MCP**. Use an auth token with
read access to the datasets the agent should query; an ingest-only token cannot
read data.

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

DASH0_AUTH_TOKEN = "YOUR_DASH0_AUTH_TOKEN"

root_agent = Agent(
    model="gemini-flash-latest",
    name="dash0_agent",
    instruction="Help users investigate their services with data from Dash0",
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://api.eu-west-1.aws.dash0.com/mcp",
                headers={"Authorization": f"Bearer {DASH0_AUTH_TOKEN}"},
            ),
        )
    ],
)
```

### Available tools

The server's tools only read data. Most of them take a `dataset` parameter,
which the agent finds with `listDatasets`. Commonly used tools:

Tool | Description
---- | -----------
`listDatasets` | List the datasets the token can read, with their technical IDs
`getServiceCatalog` | List services with their request rate, errors, and duration
`getServiceDetails` | Get one service's health, operations, and dependencies
`getMetricCatalog` | List the metrics available in a dataset
`getSpans` | Search spans by attributes and time range
`getTraceDetails` | Get a trace with its span hierarchy and events
`getLogRecords` | Get log records that match filters and a time range
`getFailedChecks` | List failed checks over a time range

See [Query Telemetry via
MCP](https://www.dash0.com/docs/dash0/ai/agent0/overview/use-agent0/query-telemetry-via-mcp)
for the full list and their parameters.

## Support and Resources

- [Dash0 Documentation](https://www.dash0.com/docs/dash0)
- [About the Dash0 MCP Server](https://www.dash0.com/docs/dash0/ai/mcp)
- [About GenAI Spans in Dash0](https://www.dash0.com/docs/dash0/telemetry/tracing/about-gen-ai-spans)
- [ADK agent activity traces](/observability/traces/)
