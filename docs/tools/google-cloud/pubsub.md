# Google Cloud Pub/Sub Toolset

The Pub/Sub toolset provides a set of tools for interacting with Google Cloud Pub/Sub. You can use these tools to publish messages to topics, pull messages from subscriptions, and acknowledge messages.

## Prerequisites

Before you can use the Pub/Sub toolset, you need to:

1.  **Enable the Pub/Sub API** for your Google Cloud project. You can do this from the [Google Cloud Console](https://console.cloud.google.com/apis/library/pubsub.googleapis.com).
2.  **Set up authentication.** The toolset uses Application Default Credentials (ADC) by default. You can set up ADC by running the following command and following the instructions:

    ```bash
    gcloud auth application-default login
    ```

    Alternatively, you can configure other authentication methods like OAuth 2.0 or service accounts. For more details, see the authentication guide.

## Usage

The following example shows how to use the `PubSubToolset` with an agent:

```python
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.pubsub.config import PubSubToolConfig
from google.adk.tools.pubsub.pubsub_credentials import PubSubCredentialsConfig
from google.adk.tools.pubsub.pubsub_toolset import PubSubToolset
import google.auth

# Initialize the tools to use the application default credentials.
# https://cloud.google.com/docs/authentication/provide-credentials-adc
application_default_credentials, project_id = google.auth.default()
credentials_config = PubSubCredentialsConfig(
    credentials=application_default_credentials
)

# You can optionally set the project_id here, or let the agent infer it from
# context/user input.
tool_config = PubSubToolConfig(project_id=project_id)

pubsub_toolset = PubSubToolset(
    credentials_config=credentials_config, pubsub_tool_config=tool_config
)

agent = LlmAgent(
    model="gemini-1.5-flash",
    tools=[pubsub_toolset],
)
```

## Tools

The `PubSubToolset` includes the following tools:

### `publish_message`

Publishes a message to a Pub/Sub topic.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `topic_name` | `str` | The name of the Pub/Sub topic (e.g., `projects/my-project/topics/my-topic`). |
| `message` | `str` | The content of the message to publish. |
| `attributes` | `dict[str, str]` (Optional) | A dictionary of attributes to attach to the message. |
| `ordering_key` | `str` (Optional) | The ordering key for the message. |

### `pull_messages`

Pulls messages from a Pub/Sub subscription.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `subscription_name` | `str` | The name of the Pub/Sub subscription (e.g., `projects/my-project/subscriptions/my-sub`). |
| `max_messages` | `int` (Optional) | The maximum number of messages to pull. Defaults to 1. |
| `auto_ack` | `bool` (Optional) | Whether to automatically acknowledge the messages. Defaults to `False`. |

### `acknowledge_messages`

Acknowledges messages on a Pub/Sub subscription.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `subscription_name` | `str` | The name of the Pub/Sub subscription (e.g., `projects/my-project/subscriptions/my-sub`). |
| `ack_ids` | `list[str]` | A list of acknowledgment IDs to acknowledge. |
