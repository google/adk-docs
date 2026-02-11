---
catalog_title: Pub/Sub Tools
catalog_description: Publish, pull, and acknowledge messages from Google Cloud Pub/Sub
catalog_icon: /adk-docs/integrations/assets/pubsub.png
catalog_tags: ["google"]
---

# Google Cloud Pub/Sub tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.22.0</span>
</div>

The `PubSubToolset` allows agents to interact with
[Google Cloud Pub/Sub](https://cloud.google.com/pubsub)
service to publish, pull, and acknowledge messages.

## Prerequisites

Before using the `PubSubToolset`, you need to:

1.  **Enable the Pub/Sub API** in your Google Cloud project.
2.  **Authenticate and authorize**: Ensure that the principal (e.g., user, service account) running the agent has the necessary IAM permissions to perform Pub/Sub operations. For more information on Pub/Sub roles, see the [Pub/Sub access control documentation](https://cloud.google.com/pubsub/docs/access-control).
3.  **Create a topic or subscription**: [Create a topic](https://cloud.google.com/pubsub/docs/create-topic) to publish messages and [create a subscription](https://cloud.google.com/pubsub/docs/create-subscription) to receive them.


## Usage

```py
--8<-- "examples/python/snippets/tools/built-in-tools/pubsub.py"
```
## Tools

The `PubSubToolset` includes the following tools:

### `publish_message`

Publishes a message to a Pub/Sub topic.

| Parameter      | Type                | Description                                                                                             |
| -------------- | ------------------- | ------------------------------------------------------------------------------------------------------- |
| `topic_name`   | `str`               | The name of the Pub/Sub topic (e.g., `projects/my-project/topics/my-topic`).                            |
| `message`      | `str`               | The message content to publish.                                                                         |
| `attributes`   | `dict[str, str]`    | (Optional) Attributes to attach to the message.                                                         |
| `ordering_key` | `str`               | (Optional) The ordering key for the message. If you set this parameter, messages are published in order. |

### `pull_messages`

Pulls messages from a Pub/Sub subscription.

| Parameter           | Type    | Description                                                                                                 |
| ------------------- | ------- | ----------------------------------------------------------------------------------------------------------- |
| `subscription_name` | `str`   | The name of the Pub/Sub subscription (e.g., `projects/my-project/subscriptions/my-sub`).                      |
| `max_messages`      | `int`   | (Optional) The maximum number of messages to pull. Defaults to `1`.                                         |
| `auto_ack`          | `bool`  | (Optional) Whether to automatically acknowledge the messages. Defaults to `False`.                            |

### `acknowledge_messages`

Acknowledges one or more messages on a Pub/Sub subscription.

| Parameter           | Type          | Description                                                                                       |
| ------------------- | ------------- | ------------------------------------------------------------------------------------------------- |
| `subscription_name` | `str`         | The name of the Pub/Sub subscription (e.g., `projects/my-project/subscriptions/my-sub`).            |
| `ack_ids`           | `list[str]`   | A list of acknowledgment IDs to acknowledge.                                                      |
