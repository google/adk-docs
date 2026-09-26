# Deferred scheduling with Gemini models

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v2.10.0</span>
</div>

Agent workloads have different latency needs. An interactive assistant must
answer immediately, but a summarization job, a bulk evaluation run, or a
document-processing pipeline can wait for capacity. Deferred scheduling lets
ADK agents queue those model calls to run on off-peak capacity instead
of competing for interactive capacity.

You can request deferred scheduling per run, using the `service_tier` setting
of `RunConfig`. The setting is part of the run configuration rather than the
model or the agent, so one agent definition can serve both interactive requests
and batch workloads.

!!! note "Deferred capacity requires allowlisted access"

    Running requests on deferred capacity requires an allowlist for your Google
    Cloud project. Request access before you use `ServiceTier.DEFERRED`.

## Get started

Deferred scheduling requires a Gemini model configured with the
Google Cloud for Gemini [Interactions API](index.md#interactions-api). Set
`use_interactions_api=True` on the model, then pass
`RunConfig(service_tier=ServiceTier.DEFERRED)` when you run the agent,
as shown in the following example:

=== "Python"

    ```python
    import asyncio

    from google.adk.agents import LlmAgent
    from google.adk.agents import RunConfig
    from google.adk.apps import App
    from google.adk.models import ServiceTier
    from google.adk.models.google_llm import Gemini
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    root_agent = LlmAgent(
        name='batch_agent',
        model=Gemini(
            model='gemini-flash-latest',
            use_interactions_api=True,  # Required for deferred scheduling
        ),
        instruction='Process input documents and produce summaries.',
    )

    app = App(name='batch_app', root_agent=root_agent)
    runner = InMemoryRunner(app=app)


    async def main() -> None:
      session = await runner.session_service.create_session(
          app_name=app.name,
          user_id='user_123',
          session_id='session_456',
      )

      # Request off-peak capacity for every model call in this run.
      run_config = RunConfig(service_tier=ServiceTier.DEFERRED)

      async for event in runner.run_async(
          user_id='user_123',
          session_id=session.id,
          new_message=types.Content(
              role='user',
              parts=[types.Part.from_text(
                  text='Summarize quarterly performance metrics.'
              )],
          ),
          run_config=run_config,
      ):
        if event.content and event.content.parts:
          for part in event.content.parts:
            if part.text:
              print(part.text)


    asyncio.run(main())
    ```

The runner submits the model call, waits for the queued work to finish, and then
yields the response event. Your code consumes events exactly as it does for a
standard run.

!!! warning "The run appears to hang while it waits"

    The `run_async()` method yields no events while the request sits in the
    queue. How long that takes depends on backend load, and ADK applies no
    upper bound. In a web UI or a terminal, the delay looks like a hang. Show a
    progress indicator, or set a
    [client deadline](#set-a-client-side-deadline).

To confirm that the tier took effect, check your application logs for these
messages:

| Log message | Level | Meaning |
| :--- | :--- | :--- |
| `Using service_tier from run_config: deferred` | `DEBUG` | ADK applied the tier to the request. |
| `Interaction <id> is queued; waiting for the result.` | `INFO` | The backend accepted the work into the queue. |
| `Interaction <id> reached status completed.` | `INFO` | The result is ready. |
| `run_config.service_tier=... has no effect for agent <name>` | `WARNING` | ADK dropped the tier. See [Troubleshooting](#troubleshooting). |

## How deferred scheduling works

Standard model requests are synchronous. ADK sends the request and the model
returns a response on the same connection. When you enable deferred scheduling
by setting `ServiceTier.DEFERRED`, ADK marks the request for background
execution and the backend queues it, returning an interaction ID immediately
instead of a result.

ADK then waits for that result, checking the queued work with exponential
backoff and absorbing transient read failures until it reaches a final status.
It converts that result to a normal response event and yields it. This loop is
internal: it does not surface interaction IDs, and you do not need to write any
retrieval code. It does add a few seconds of polling delay on top of the queue
wait, so deferred scheduling should not be used for short, latency-sensitive
calls.

The following properties of the wait affect how you design your agent:

*   **ADK sets no client-side deadline.** The backend's completion timeout on
    the interaction is the only bound on the wait. To stop sooner, see
    [Set a client-side deadline](#set-a-client-side-deadline).
*   **Each model turn queues separately.** In an agent that calls tools, every
    turn creates its own interaction, so total latency is the sum of every
    turn's queue wait rather than a single wait for the run.

## Configuration options

The `service_tier` setting of `RunConfig` selects the capacity pool for every
model call in a run:

| Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `service_tier` | `Optional[ServiceTier \| str]` | `None` | Serving tier for the model calls of this run. |

The `ServiceTier` enum defines the following tiers:

*   `ServiceTier.DEFERRED`: Queues the call to run on off-peak capacity. The
    call waits for room instead of failing when capacity is tight. No other
    tier changes how ADK executes the request, and it cannot be combined with
    streaming.
*   `ServiceTier.FLEX`: Best-effort capacity at a lower cost, with no latency
    guarantee.
*   `ServiceTier.STANDARD`: The default tier.
*   `ServiceTier.PRIORITY`: Reserved capacity for latency-sensitive calls.

Leaving `service_tier` unset omits the field from the request entirely, which is
equivalent to `ServiceTier.STANDARD`. The `ServiceTier` enum subclasses `str`,
so you can pass a plain string such as `'deferred'` in place of an enum member.
The string form also lets you use a tier the backend supports before ADK
defines a constant for it.

## Advanced usage

The following sections describe how to bound the wait time for a deferred run
with a client-side deadline and how to request deferred scheduling when serving
an agent over HTTP.

### Set a client-side deadline {#set-a-client-side-deadline}

A deferred request waits for off-peak capacity, and its duration depends on
backend load. To cap the total elapsed time, wrap the run in an
`asyncio.timeout()`, which requires Python 3.11 or later:

=== "Python"

    ```python
    import asyncio
    import logging

    from google.adk.agents import RunConfig
    from google.adk.models import ServiceTier
    from google.genai import types

    logger = logging.getLogger(__name__)

    # Continues from the Get started example, reusing runner and session.
    message = types.Content(
        role='user',
        parts=[types.Part.from_text(text='Generate a quarterly summary.')],
    )
    run_config = RunConfig(service_tier=ServiceTier.DEFERRED)

    try:
      async with asyncio.timeout(300):
        async for event in runner.run_async(
            user_id='user_123',
            session_id=session.id,
            new_message=message,
            run_config=run_config,
        ):
          if event.content and event.content.parts:
            for part in event.content.parts:
              if part.text:
                print(part.text)
    except TimeoutError:
      logger.error('Deferred run exceeded the 300 second client deadline.')
    ```

!!! danger "Client deadlines do not cancel requests"

    Timing out stops ADK from polling for the result, but does not stop the
    backend. The queued request runs to completion and consumes billed usage,
    and you cannot retrieve its output afterward. Treat a timed-out turn as
    forfeited, and do not use a client deadline to limit usage.

### Request deferred scheduling over HTTP

An agent you serve with `adk api_server` accepts `service_tier` in the request
body of the `/run` and `/run_sse` endpoints:

```json
{
  "app_name": "batch_app",
  "user_id": "user_123",
  "session_id": "session_456",
  "new_message": {
    "role": "user",
    "parts": [{"text": "Summarize batch results."}]
  },
  "service_tier": "deferred"
}
```

For `/run_sse` requests, you must also set `"streaming": false`. Combining
`"service_tier": "deferred"` with `"streaming": true` returns HTTP 422.
An HTTP request holds the connection open for the whole queue wait, which makes
the hosting platform's request timeout the effective limit on a deferred run:

*   **Raise proxy and ingress timeouts.** Load balancers and ingress
    controllers close long-running backend connections by default. Check the
    limits for your platform, such as the
    [Cloud Run request timeout](https://cloud.google.com/run/docs/configuring/request-timeout),
    and raise them to cover your expected queue wait.
*   **A client disconnect cancels retrieval, not execution.** When the
    connection closes, the server cancels its polling task. The queued request
    still runs and still consumes billed usage, and you lose its output.

For deferred workloads that may wait a long time, deploy to
[Agent Runtime](/deploy/agent-runtime/) on Google Cloud Agent Platform instead.
Agent Runtime runs the invocation in a managed container and does not hold an
HTTP connection open for it.

## Limitations

The following limitations apply to deferred scheduling:

*   **Allowlisted access:** Deferred capacity requires an allowlist for your
    Google Cloud project.
*   **Gemini and the Interactions API only:** Deferred scheduling works only
    with a `Gemini` model that sets `use_interactions_api=True`. Any other
    model, including a custom `BaseLlm` subclass, ignores the tier.
*   **Not compatible with streaming:** Constructing
    `RunConfig(service_tier=ServiceTier.DEFERRED, streaming_mode=StreamingMode.SSE)`
    raises a `pydantic.ValidationError`.
*   **`ManagedAgent` class ignores the tier:** It runs its own interaction
    loop and never reads `service_tier`.
*   **No resumption across restarts:** ADK does not persist in-flight
    interaction IDs, and offers no way to reattach a run to a queued
    interaction. If the client process stops, ADK abandons the pending work and
    the next run creates a new interaction.

## Troubleshooting

The following sections describe some common issues when using deferred
scheduling, and how to resolve them.

### ADK ignores the tier and the run still succeeds

If the agent's model is not a `Gemini` instance with
`use_interactions_api=True`, ADK drops the tier, logs a warning once per run,
and executes the call on standard capacity. The run succeeds, so the log is the
only signal:

```text
run_config.service_tier=... has no effect for agent <name>: its model does not
use the interactions API, which is the only path with a serving tier. Set
use_interactions_api=True on the model to apply the tier.
```

The warning is intentional. In a multi-agent run, only some agents may be on the
Interactions API, so an unusable tier warns rather than raises. Search your logs
for `has no effect for agent` to find models that need
`use_interactions_api=True`.

### OpenAI `service_tier` field

The `OpenAIResponsesLlm` class also has a `service_tier` field. It is an
unrelated setting: you set it on the model rather than on the run, and
`RunConfig.service_tier` does not feed it. Setting one has no effect on the
other.

## Additional resources

*   [Gemini Interactions API](index.md#interactions-api)
*   [Runtime Configuration](/runtime/runconfig/)
*   [Interactions API code sample](https://github.com/google/adk-python/tree/main/contributing/samples/models/interactions_api)
