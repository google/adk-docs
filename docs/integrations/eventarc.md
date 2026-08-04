---
catalog_title: Google Cloud Eventarc Tools
catalog_description: Publish structured CloudEvents to message buses with schema validation
catalog_icon: /integrations/assets/eventarc.png
catalog_tags: ["google"]
---

# Google Cloud Eventarc tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v2.6.0</span><span class="lst-preview">Experimental</span>
</div>

The `EventarcToolset` allows agents to interact with [Google Cloud Eventarc](https://cloud.google.com/eventarc) to asynchronously publish structured [CloudEvents](https://cloudevents.io) to Eventarc Message Buses. The toolset provides built-in connection pooling and caching across invocations, and it supports both general-purpose event publishing and domain-specific, schema-enforced event tools.

!!! example "Experimental"
    This feature is experimental and may be updated in future releases.

## Prerequisites

Before using the `EventarcToolset`, you need to complete the following setup steps:

1.  **Enable the Eventarc APIs**: Enable the Eventarc and Eventarc Publishing APIs in your Google Cloud project:

    ```bash
    gcloud services enable eventarc.googleapis.com eventarcpublishing.googleapis.com
    ```

2.  **Authenticate and authorize**: Ensure that the principal running the agent has the necessary IAM permissions to publish messages to Eventarc Message Buses (for example, the `roles/eventarc.publisher` role). For more information on Eventarc IAM roles, see the [Eventarc access control documentation](https://cloud.google.com/eventarc/docs/access-control). To set up local development credentials, see [Provide Application Default Credentials](https://cloud.google.com/docs/authentication/provide-credentials-adc).
3.  **Create a Message Bus**: Create a target Eventarc Advanced Message Bus in your Google Cloud project to receive published events:

    ```bash
    gcloud eventarc message-buses create my-bus \
        --location=us-central1 \
        --logging-config=DEBUG
    ```

## Use with agent

The following example shows how to configure and equip an agent with the `EventarcToolset` to publish CloudEvents:

```py
--8<-- "examples/python/snippets/tools/built-in-tools/eventarc.py"
```

## Tools

The `EventarcToolset` includes the following general-purpose publishing tool by default:

### `publish_message`

Publishes a structured CloudEvent to a Google Cloud Eventarc Advanced Message Bus.

| Parameter           | Type               | Description                                                                                                                                              |
| ------------------- | ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bus`               | `str`              | The full resource name of the Eventarc Message Bus (for example, `projects/my-project/locations/us-central1/messageBuses/my-bus`).                           |
| `type`              | `str`              | The CloudEvents type identifier representing the occurrence (for example, `com.example.user.signup`).                                                    |
| `source`            | `str`              | The CloudEvents source URI identifying the context in which an event happened (for example, `//my-service/auth`).                                        |
| `data`              | `dict \| str \| Any` | (Optional) The event payload data to include in the CloudEvent.                                                                                          |
| `datacontenttype`   | `str`              | (Optional) The media type of `data` (for example, `application/json`). Defaults to `application/json` when dictionary or JSON data is provided.             |
| `subject`           | `str`              | (Optional) The subject of the event in the context of the event producer.                                                                                |
| `id`                | `str`              | (Optional) A unique identifier for the event. If not provided, a UUID is automatically generated.                                                        |
| `time`              | `str`              | (Optional) Timestamp of when the occurrence happened in RFC 3339 format. If not provided, the current UTC timestamp is used.                             |
| `specversion`       | `str`              | (Optional) The CloudEvents specification version. Defaults to `1.0`.                                                                                     |
| `is_base64_encoded`         | `bool`             | (Optional) Whether `data` is base64-encoded binary data. Defaults to `False`.                                                                            |
| `include_tracing_extension` | `bool`             | (Optional) Whether to automatically extract and inject distributed tracing context into the CloudEvent's extension attributes. Defaults to `False`.      |
| `custom_attributes`         | `dict[str, str]`   | (Optional) Additional custom CloudEvent extension attributes to attach to the event.                                                                     |

## Domain-specific publish tools

In production multi-agent architectures, allowing an LLM to freely populate routing parameters (`bus`, `type`, `source`) can lead to hallucinated destinations or malformed event schemas. The `EventarcToolset.create_publish_tool` factory method enables you to create domain-specific, strict-schema publishing tools.

By creating a domain-specific tool, you can bind routing attributes using `CloudEventAttributesBinding` while enforcing a strict Pydantic model for the event payload (`payload_schema`). This guarantees that generated events match your business domain and are routed only to authorized message buses.

### Use with agent

```py
--8<-- "examples/python/snippets/tools/built-in-tools/eventarc_domain_specific.py"
```

### Parameters for `create_publish_tool`

The `create_publish_tool` method accepts the following keyword-only arguments:

| Parameter               | Type                                                                       | Description                                                                                                                                                                                |
| ----------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `name`                  | `str`                                                                      | The function tool name exposed to the LLM (for example, `complete_outreach_static`).                                                                                                         |
| `description`           | `str`                                                                      | A natural-language description instructing the LLM when to call this tool and what action it performs.                                                                                     |
| `bus`                   | `str \| Callable[[Any], str] \| AgentProvided`                             | The target Eventarc Message Bus. Can be a static URI string, a runtime callable evaluated against tool context, or an `AgentProvided` instance to prompt the LLM to supply it.             |
| `ce_attributes_binding` | `CloudEventAttributesBinding`                                              | Binding rules for CloudEvent attributes (`type`, `source`, `subject`, `datacontenttype`, `time`, `id`, `specversion`, `custom_attributes`).                                                               |
| `payload_schema`        | `type[pydantic.BaseModel] \| None`                                         | (Optional) A Pydantic schema class defining the structured event payload. When specified, the tool signature requires an `event_data` parameter conforming to this model. If not provided (or `None`), no `event_data` parameter is added to the tool signature, and the tool publishes a notification-only CloudEvent without a data payload body. |

### CloudEvent attribute bindings and sentinels

The `CloudEventAttributesBinding` dataclass configures how individual CloudEvent fields are populated. Each attribute (`type`, `source`, `datacontenttype`, `subject`, `time`, `id`, `specversion`, `custom_attributes`) can be assigned one of the following binding mechanisms:

| Binding Type       | Example                                     | Exposed to LLM | Description                                                                                                                                           |
| ------------------ | ------------------------------------------- | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Static String**  | `type="vendor_outreach.completed"`          | No             | Enforces a fixed literal string. The attribute is hidden from the LLM signature and automatically applied on every call.                              |
| **Runtime Lambda** | `source=lambda ctx: f"//agent/{ctx.id}"`    | No             | A callable (`Callable[[Any], str]`) evaluated dynamically at execution time using the tool runtime context. Hidden from the LLM signature.            |
| **`AgentProvided`**| `subject=AgentProvided("Customer ID")`      | Yes            | Instructs ADK to expose the attribute as an explicit parameter in the function signature so the LLM can provide it. Accepts a `description` string.     |
| **`MISSING`**      | `time=MISSING`                              | No             | The default sentinel for optional attributes. Indicates default behavior applies (for example, automatically generating the current UTC timestamp for `time` or a UUID for `id`). |
| **`OMIT`**         | `time=OMIT`                                 | No             | Explicitly excludes an optional attribute from the generated CloudEvent. Mandatory attributes (`type`, `source`, `bus`) cannot be set to `OMIT`.                                      |

#### Example: Understanding `MISSING` versus `OMIT`

To understand the difference between `MISSING` and `OMIT`, consider how they affect an optional CloudEvent attribute such as `time`:

-   **`time=MISSING` (default behavior)**: When you set `time=MISSING` (or leave `time` unspecified), the toolset applies its built-in default behavior. For `time`, it automatically generates and includes the current UTC timestamp formatted in RFC 3339 (for example, `"time": "2026-07-31T20:20:00Z"`).
-   **`time=OMIT`**: When you explicitly set `time=OMIT`, the `time` field is completely excluded from the published CloudEvent payload. Use `OMIT` when downstream event consumers do not require or expect optional attributes.

```py
from google.adk.integrations.eventarc import (
    CloudEventAttributesBinding,
    MISSING,
    OMIT,
)

# 1. Using MISSING (default): CloudEvent automatically includes the current UTC timestamp
binding_with_timestamp = CloudEventAttributesBinding(
    type="vendor_outreach.completed",
    source="//my-agent/outreach",
    time=MISSING,  # Results in "time": "2026-07-31T20:20:00Z"
)

# 2. Using OMIT: CloudEvent will NOT include a 'time' attribute
binding_without_timestamp = CloudEventAttributesBinding(
    type="vendor_outreach.completed",
    source="//my-agent/outreach",
    time=OMIT,  # The 'time' field is excluded from the published event
)
```

## Additional resources

- [Google Cloud Eventarc documentation](https://cloud.google.com/eventarc/docs).
- [ADK Python GitHub repository](https://github.com/google/adk-python).
