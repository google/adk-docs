# Ambient Agents

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-go">Go</span>
</div>

ADK supports **ambient agents**, autonomous agents that process data, monitor
events, and respond asynchronously without human intervention. Use ambient
agents to:

- **React to cloud events.** Process a file when it's uploaded to
  [Cloud Storage](https://cloud.google.com/storage), respond to database
  changes, or handle audit log entries.
- **Process messages from a queue.** Analyze incoming support tickets,
  moderate content, classify documents, or run QA as items arrive.
- **Run on a schedule.** Generate daily reports, run periodic monitoring
  checks, or process batch jobs at regular intervals.
- **Monitor infrastructure.** React to a continuous stream of events across
  your infrastructure and act on changes autonomously.

## Getting results from ambient agents

Because ambient agents run without human interaction, you need to route their
outputs to a notification channel. Common patterns include:

- **[Structured logging](../observability/logging.md).** Write JSON logs and
  configure [Cloud Monitoring](https://cloud.google.com/monitoring/support/notification-options)
  alerts to notify via email, Slack, or PagerDuty.
- **[Pub/Sub](https://cloud.google.com/pubsub).** Publish results to a topic
  for downstream services to consume.
- **[Application Integration](https://cloud.google.com/application-integration/docs/listen-pub-sub-topic-send-email).**
  Route agent outputs to email, Jira, or other systems.

## How to build ambient agents

ADK provides two approaches:

| | [`/run`](api-server.md) | Trigger endpoints |
| :--- | :--- | :--- |
| **Event sources** | Any (Pub/Sub, webhooks, cron, custom services) | [Cloud Pub/Sub](https://cloud.google.com/pubsub), [Eventarc](https://cloud.google.com/eventarc) ([Standard](https://cloud.google.com/eventarc/standard/docs/overview) and [Advanced](https://cloud.google.com/eventarc/advanced/docs/overview)) |
| **Payload parsing** | You handle it | Automatic (Base64 decoding, CloudEvent parsing) |
| **Session creation** | Enable `--auto_create_session` | Automatic (one per event) |
| **Session storage** | Your configured [`SessionService`](../sessions/session/index.md) | Your configured [`SessionService`](../sessions/session/index.md) |
| **Concurrency control** | You handle it | Built-in semaphore with configurable limit |
| **Retry logic** | You handle it | Exponential backoff with jitter for transient errors |
| **Best for** | Custom integrations, non-GCP sources | GCP-native event-driven workloads |

## Using `/run`

Use the [`/run`](api-server.md) endpoint when you need full control over
the integration or are working with non-GCP event sources. Enable
`--auto_create_session` so that sessions are created automatically, then
connect any HTTP client to call `/run` when events arrive.

```bash
adk api_server --auto_create_session path/to/your/agent
```

This pattern works with any event source that can make an HTTP request.

??? "Example: Processing incoming webhooks"

    The following [Cloud Run function](https://cloud.google.com/functions/docs/writing/write-event-driven-functions)
    receives a webhook from an external service (for example, GitHub) and
    forwards it to your agent:

    ```python
    import json
    import uuid

    import functions_framework
    import requests

    AGENT_URL = "https://my-agent-service-xxxxx.run.app"

    @functions_framework.http
    def handle_webhook(request):
        """Cloud Run function that receives webhooks and forwards to the agent."""
        payload = request.get_json(silent=True) or {}

        requests.post(
            f"{AGENT_URL}/apps/my_agent/run",
            json={
                "app_name": "my_agent",
                "user_id": payload.get("account", "webhook-caller"),
                "session_id": str(uuid.uuid4()),
                "new_message": {
                    "role": "user",
                    "parts": [{"text": json.dumps(payload)}],
                },
            },
        )

        return ("ok", 200)
    ```

??? "Example: Send an event with curl"

    ```bash
    curl -X POST http://localhost:8000/apps/my_agent/run \
      -H "Content-Type: application/json" \
      -d '{
        "app_name": "my_agent",
        "user_id": "webhook-caller",
        "session_id": "session-123",
        "new_message": {
          "role": "user",
          "parts": [{"text": "{\"order_id\": \"1234\", \"status\": \"new\"}"}]
        }
      }'
    ```

## Using trigger endpoints

Use trigger endpoints when your event sources are Pub/Sub or Eventarc and you
want ADK to handle payload parsing, session creation, concurrency, and retries.

### How events are processed

Pub/Sub and Eventarc deliver events to your agent as HTTP POST requests.
When a trigger endpoint receives an event, it:

1. **Parses the request** according to the source format (Pub/Sub push message
   or CloudEvent).
2. **Decodes the payload.** Base64-encoded message data is decoded and, if
   possible, parsed as JSON.
3. **Creates a session** automatically with a generated UUID. Unlike the `/run`
   endpoint, you do not need to enable `--auto_create_session` — trigger
   endpoints always create a new session per event.
4. **Runs your agent** with the decoded event as a user message.
5. **Returns a status code.** A `200` response tells Pub/Sub or Eventarc that
   the event was processed successfully. A `500` response signals a failure,
   and the event source retries delivery based on its retry policy.

### Supported sources

| Source | Endpoint | Description |
| :----- | :------- | :---------- |
| **Pub/Sub** | `/apps/{app_name}/trigger/pubsub` | Receives messages from a [Pub/Sub push subscription](https://cloud.google.com/pubsub/docs/push). |
| **Eventarc** | `/apps/{app_name}/trigger/eventarc` | Receives [CloudEvents](https://cloudevents.io/) delivered by [Eventarc](https://cloud.google.com/eventarc) ([Standard](https://cloud.google.com/eventarc/standard/docs/overview) or [Advanced](https://cloud.google.com/eventarc/advanced/docs/overview)), supporting both structured and binary content modes. |

### Example agent

=== "Python"
    The following agent processes events from a trigger endpoint. It uses a
    `parse_event` tool to extract the event data and attributes, then analyzes
    the contents.

    ???+ "Agent code (`event_processing_agent/agent.py`)"

        ```python
        --8<-- "examples/python/snippets/runtime/triggers/event_processing_agent/agent.py:event_processor"
        ```

=== "Go"
    The following agent processes events from a trigger endpoint. It extracts the event data and attributes, then analyzes the contents.

    ???+ "Agent code (`event_processing_agent.go`)"

        ```go
        --8<-- "examples/go/snippets/runtime/triggers/event_processing_agent.go:event_processor"
        ```

### Enable triggers

=== "Python"

    Trigger endpoints are disabled by default. Enable them with the
    `--trigger_sources` flag:

    ```shell
    adk api_server --trigger_sources "pubsub,eventarc" path/to/your/agent
    ```

    For production deployments, you can enable triggers programmatically in a
    custom FastAPI entry point:

    ???+ "Deployment entry point (`main.py`)"

        === "Python"
            ```python
            --8<-- "examples/python/snippets/runtime/triggers/main.py:triggers"
            ```

=== "Go"

    Trigger endpoints are disabled by default. Enable them with the
    corresponding trigger flag:

    ```shell
    go run agent.go web api pubsub eventarc
    ```

### Try it locally

**1. Start the server with triggers enabled:**

=== "Python"

    ```bash
    adk api_server --trigger_sources "pubsub" event_processing_agent
    ```

=== "Go"

    ```bash
    go run event_processing_agent.go web api pubsub
    ```

**2. Send a test event:**

```bash
curl -X POST http://localhost:8000/apps/event_processing_agent/trigger/pubsub \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "data": "eyJvcmRlcl9pZCI6ICIxMjM0IiwgInN0YXR1cyI6ICJuZXcifQ==",
      "attributes": {"source": "orders-service"}
    },
    "subscription": "projects/my-project/subscriptions/orders-sub"
  }'
```

The Base64 value decodes to `{"order_id": "1234", "status": "new"}`.

A successful response:

```json
{"status": "success"}
```

## Trigger sources

### Parameter mapping

The `/run` endpoint requires you to provide `app_name`, `user_id`, and
`session_id`. Trigger endpoints derive these automatically:

| Parameter | Source |
| :-------- | :----- |
| `app_name` | Extracted from the URL path (`/apps/{app_name}/trigger/...`) |
| `session_id` | Auto-generated UUID per event |
| `user_id` | Pub/Sub: the `subscription` field. Eventarc: the `source` or `ce-source` header. |

### Message format

All trigger endpoints normalize the incoming event into a consistent JSON
structure before passing it to your agent as the user message:

```json
{
  "data": "<decoded event payload>",
  "attributes": {"key": "value"}
}
```

- **`data`**: The decoded event payload. If the original data is JSON, it is
  parsed into a structured object. Otherwise, it is passed as a plain string.
- **`attributes`**: Key-value metadata from the event source (for example, Pub/Sub
  message attributes or CloudEvents headers like `ce-type`, `ce-source`).

Your agent receives this JSON string as the input message and can parse it to
extract the data and attributes.

### Pub/Sub

The Pub/Sub trigger endpoint processes messages from a
[Pub/Sub push subscription](https://cloud.google.com/pubsub/docs/push). Use it
when your applications or services publish messages to a topic, for example:

- A support portal publishes incoming tickets for triage and routing.
- A content pipeline sends documents for classification or moderation.
- A monitoring service publishes alerts for automated analysis.

#### Request format

Pub/Sub push subscriptions send requests in this format:

```json
{
  "message": {
    "data": "eyJvcmRlcl9pZCI6ICIxMjM0IiwgInN0YXR1cyI6ICJuZXcifQ==",
    "attributes": {"source": "orders-service"},
    "messageId": "123456789",
    "publishTime": "2026-04-08T12:00:00Z"
  },
  "subscription": "projects/my-project/subscriptions/my-sub"
}
```

The `data` field is Base64-encoded. The trigger endpoint decodes it
automatically.

#### Response

| HTTP Status | Meaning |
| :---------- | :------ |
| **200** | Event processed successfully. Pub/Sub acknowledges the message. |
| **400** | Invalid request (malformed Base64 encoding). Message is not retried. |
| **500** | Processing failed (transient or non-transient agent errors). Pub/Sub retries delivery based on its [retry policy](https://cloud.google.com/pubsub/docs/handling-failures). Configure a [dead-letter queue](https://cloud.google.com/pubsub/docs/dead-letter-topics) to catch messages that fail repeatedly. |

### Eventarc

The Eventarc trigger endpoint processes
[CloudEvents](https://cloud.google.com/eventarc/docs/cloudevents) delivered by
[Eventarc](https://cloud.google.com/eventarc), both
[Standard](https://cloud.google.com/eventarc/standard/docs/overview) and
[Advanced](https://cloud.google.com/eventarc/advanced/docs/overview) editions.
Use it to react to events across Google Cloud, for example:

- A file is uploaded to [Cloud Storage](https://cloud.google.com/storage) (classify, summarize, or extract data from documents).
- A record is written to [BigQuery](https://cloud.google.com/bigquery) (run anomaly detection or generate alerts).
- An [Audit Log](https://cloud.google.com/logging/docs/audit) entry is created (flag policy violations or suspicious activity).

Both content modes are supported:

- **Binary content mode** (Eventarc default): CloudEvents attributes are sent
  as `ce-*` HTTP headers, and the body contains the event data (typically a
  Pub/Sub message wrapper).
- **Structured content mode**: All CloudEvents attributes and data are in the
  JSON body.

??? "Test with curl (structured mode)"

    ```bash
    curl -X POST http://localhost:8000/apps/my_agent/trigger/eventarc \
      -H "Content-Type: application/json" \
      -d '{
        "specversion": "1.0",
        "type": "google.cloud.storage.object.v1.finalized",
        "source": "//storage.googleapis.com/projects/my-project",
        "id": "event-123",
        "data": {
          "bucket": "my-bucket",
          "name": "uploads/document.pdf"
        }
      }'
    ```

??? "Test with curl (binary mode)"

    ```bash
    curl -X POST http://localhost:8000/apps/my_agent/trigger/eventarc \
      -H "Content-Type: application/json" \
      -H "ce-type: google.cloud.storage.object.v1.finalized" \
      -H "ce-source: //storage.googleapis.com/projects/my-project" \
      -H "ce-id: event-456" \
      -H "ce-specversion: 1.0" \
      -d '{
        "message": {
          "data": "eyJidWNrZXQiOiAibXktYnVja2V0IiwgIm5hbWUiOiAiZG9jLnBkZiJ9",
          "attributes": {"eventType": "OBJECT_FINALIZE"}
        },
        "subscription": "projects/my-project/subscriptions/eventarc-sub"
      }'
    ```

#### Response

| HTTP Status | Meaning |
| :---------- | :------ |
| **200** | Event processed successfully. Eventarc acknowledges delivery. |
| **500** | Processing failed. Eventarc retries delivery based on its retry policy. |

## Configuration

### Concurrency control

Trigger endpoints use a semaphore to limit the number of concurrent agent
invocations. This prevents your agent from exceeding your LLM model quota
during bursts of events.

=== "Python"

    | Setting | Default | Environment Variable |
    | :------ | :------ | :------------------- |
    | Max concurrent invocations | 10 | `ADK_TRIGGER_MAX_CONCURRENT` |

=== "Go"

    | Setting | Default | Flag |
    | :------ | :------ | :------------------- |
    | Max concurrent invocations | 10 | `--trigger_max_concurrent_runs` |

When the concurrency limit is reached, incoming requests are queued and processed
as slots become available. Concurrency control is per process. If you deploy
multiple Cloud Run instances, each instance maintains its own independent
semaphore.

=== "Python"

    ```bash
    # Allow up to 5 concurrent agent invocations
    export ADK_TRIGGER_MAX_CONCURRENT=5
    ```

=== "Go"

    ```bash
    go run event_processing_agent.go web api pubsub --trigger_max_concurrent_runs=5
    ```

### Automatic retry with backoff

Trigger endpoints include built-in retry logic for transient errors such as
`429 RESOURCE_EXHAUSTED` responses. When a transient error is detected, the
request is retried with exponential backoff and jitter.

=== "Python"

    | Setting | Default | Environment Variable |
    | :------ | :------ | :------------------- |
    | Max retry attempts | 3 | `ADK_TRIGGER_MAX_RETRIES` |
    | Base backoff delay | 1.0s | `ADK_TRIGGER_RETRY_BASE_DELAY` |
    | Max backoff delay | 30.0s | `ADK_TRIGGER_RETRY_MAX_DELAY` |

=== "Go"

    | Setting | Default | Flag |
    | :------ | :------ | :------------------- |
    | Max retry attempts | 3 | `--trigger_max_retries` |
    | Base backoff delay | 1.0s | `--trigger_base_delay` |
    | Max backoff delay | 30.0s | `--trigger_max_delay` |

If all retries are exhausted, the endpoint returns HTTP 500, signaling
Pub/Sub or Eventarc to retry delivery at a higher level.
Non-transient errors fail immediately without retries.

### Error handling and disaster recovery

Disaster recovery for trigger-based workloads is handled by the triggering
service, not by ADK:

- If your agent crashes or returns an error, Pub/Sub or Eventarc does not
  receive an acknowledgement and automatically redelivers the message.
- After maximum retries are exhausted, unprocessed messages move to a
  [dead-letter queue (DLQ)](https://cloud.google.com/pubsub/docs/dead-letter-topics)
  if configured.
- Each redelivery creates a new session. Trigger workloads are stateless
  by design.

### Timeout considerations

All trigger endpoints process synchronously and wait for your agent to
complete before returning a response. This is by design: keeping the HTTP
request alive ensures that the hosting infrastructure does not terminate the
process while your agent is still working. The synchronous response code
(200 or 500) is what allows Pub/Sub and Eventarc to correctly acknowledge
success or trigger a retry.

The maximum processing time is governed by the upstream service:

| Service | Max Timeout |
| :------ | :---------- |
| Pub/Sub push | 10 minutes (ack deadline) |
| Eventarc | 10 minutes ([Standard](https://cloud.google.com/eventarc/standard/docs/overview) uses Pub/Sub as transport; [Advanced](https://cloud.google.com/eventarc/advanced/docs/overview) delivers via pipeline) |

Trigger endpoints are designed for agents that complete within 10 minutes.
This is suitable for processing individual events, running validations,
classifying documents, and writing results to downstream services.

!!! warning "Long-running agents"
    Trigger endpoints are not suitable for agents that take more than 10
    minutes to complete. For long-running workloads, use
    [Pub/Sub pull subscriptions](https://cloud.google.com/pubsub/docs/pull),
    [Cloud Run Jobs](https://cloud.google.com/run/docs/create-jobs), or a
    worker pool architecture instead.

### Session lifecycle

Sessions follow the same pattern as all other ADK entry points. They are
created through your configured
[`SessionService`](../sessions/session/index.md). By default, ADK uses
`InMemorySessionService`, which makes trigger sessions ephemeral: created per
event and discarded after processing.

If you configure a persistent `SessionService` (for example, `DatabaseSessionService`),
trigger sessions are stored automatically. This can be useful for auditing,
debugging, and post-mortem analysis of event-driven workloads.

## Deploy

The examples below use [Cloud Run](https://cloud.google.com/run) as the
deployment target. Cloud Run is currently the recommended platform for
deploying ambient agents with trigger endpoints.

!!! note "Authentication and security"
    Trigger endpoints are standard HTTP routes within the ADK web server.
    Authentication and security are enforced at the deployment level, the
    same as any other ADK endpoint. When deployed with authentication enabled
    (recommended), all endpoints require valid credentials. GCP services
    authenticate using [service account](https://cloud.google.com/iam/docs/service-accounts)
    identities. See each service's documentation for details.

=== "Python"

    Deploy your agent to Cloud Run with triggers enabled using the
    `--trigger_sources` flag:

    ```bash
    adk deploy cloud_run \
      --project=$GOOGLE_CLOUD_PROJECT \
      --region=$GOOGLE_CLOUD_LOCATION \
      --trigger_sources="pubsub,eventarc" \
      path/to/your/agent
    ```

=== "Go"

    Deploy your agent to Cloud Run with triggers enabled using the corresponding trigger flag (all the settings are prefixed with trigger type)

    ```bash
    adk deploy cloud_run \
      --project=$GOOGLE_CLOUD_PROJECT \
      --region=$GOOGLE_CLOUD_LOCATION \
      --pubsub \
      --pubsub_max_concurrent_runs=5 \
      --eventarc \
      --eventarc_max_concurrent_runs=5
    ```

After deployment, connect the appropriate GCP infrastructure to your agent's
trigger endpoint:

- **Pub/Sub**: Create a [push subscription](https://cloud.google.com/pubsub/docs/push)
  pointing to `/apps/{app_name}/trigger/pubsub`.
- **Eventarc**: Create an [Eventarc Standard trigger](https://docs.cloud.google.com/eventarc/standard/docs/event-providers-targets)
  or an [Eventarc Advanced pipeline](https://cloud.google.com/eventarc/advanced/docs/overview)
  routing to `/apps/{app_name}/trigger/eventarc`.
- **Cloud Scheduler**: Create a [scheduler job](https://cloud.google.com/scheduler/docs/creating)
  that publishes to your Pub/Sub topic on a cron schedule.

See [Deploy to Cloud Run](../deploy/cloud-run.md) for full deployment
instructions.

## What's next?

- Learn how to [deploy your agent to Cloud Run](../deploy/cloud-run.md)
- Explore [API server endpoints](api-server.md) for interactive agent invocations
- Use the [Pub/Sub toolset](../integrations/pubsub.md) to give your agent the ability to publish and pull messages
