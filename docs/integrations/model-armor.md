---
catalog_title: Model Armor
catalog_description: Screen agent input and output against Google Cloud security templates
catalog_icon: /integrations/assets/model-armor.png
catalog_tags: ["google"]
---

# Model Armor plugin for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v2.8.0</span>
</div>

[Model Armor](https://cloud.google.com/security-command-center/docs/model-armor-overview)
is a Google Cloud service that inspects text for prompt injection and jailbreak attempts,
harmful content, and sensitive data. You define what to look for in a server-side policy
called a template, and the service returns a verdict for each piece of text you send it. The
`ModelArmorPlugin` class ships with ADK and calls that service from the model callbacks.
It screens user input before the model sees it and model output before the user does,
replacing matched content with a safe message.

## Use cases

- **Prompt injection and jailbreak defense**: Screen every user turn against a prompt
  template before the model acts on it, so the agent refuses a crafted message instead of
  obeying it.
- **Sensitive data and harmful content filtering**: Screen model output against a response
  template to catch answers that leak data or breach content policy before delivery.
- **Uniform policy across agents**: Register one plugin on the `App` and every agent it
  runs inherits the same screening, including
  [live voice agents](../live/guardrails.md).

## Prerequisites

- A Google Cloud project with the Model Armor API enabled, and at least one template
  created. See the [Model Armor documentation](https://cloud.google.com/security-command-center/docs/manage-model-armor-templates).
- Application Default Credentials with access to Model Armor
  (`gcloud auth application-default login`).
- [ADK](https://adk.dev) >= 2.8.0

## Installation

```bash
pip install 'google-adk[gcp]'
```

There is no separate `model-armor` extra. The plugin ships with ADK, and the `gcp` extra
supplies the `google-cloud-modelarmor` client it needs.

## Use with agent

Register the plugin on an `App` with the templates it should screen against:

```python
from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.integrations.model_armor import ModelArmorConfig
from google.adk.integrations.model_armor import ModelArmorPlugin

agent = LlmAgent(
    model="gemini-flash-latest",
    name="screened_agent",
    instruction="You are a helpful assistant.",
)

app = App(
    name="model_armor_demo",
    root_agent=agent,
    plugins=[
        ModelArmorPlugin(
            config=ModelArmorConfig(
                prompt_template_name=(
                    "projects/my-project/locations/us-central1/templates/my-prompt-template"
                ),
                response_template_name=(
                    "projects/my-project/locations/us-central1/templates/my-response-template"
                ),
            )
        )
    ],
)
```

Template names must be full resource paths in the form
`projects/{project}/locations/{location}/templates/{template}`. The plugin reads the
location out of the path to pick a regional endpoint, so both templates must live in the
same region. A short name or a mismatched pair raises `ValueError` when the plugin is
constructed.

Each template is optional, and setting only one screens only that direction:

```python
config = ModelArmorConfig(
    prompt_template_name=(
        "projects/my-project/locations/us-central1/templates/my-prompt-template"
    ),
)
```

Screening covers the most recent user content and the model's reply. Tool results reach the
request as a `function_response` part, which the plugin skips.

## Configuration

| Option | Default | Description |
| :--- | :--- | :--- |
| `prompt_template_name` | `None` | Template used to screen user input. Unset means input is not screened. |
| `response_template_name` | `None` | Template used to screen model output. Unset means output is not screened. |
| `input_blocked_message` | See below | Replacement text shown when user input is blocked. |
| `output_blocked_message` | See below | Replacement text shown when model output is blocked. |
| `block_on_screening_failure` | `True` | Whether to block content that could not be screened. |

Both messages default to `"I'm sorry, but I can't help with that request."`, and at least one
template name must be set or the config raises a validation error.

Screening fails when the Model Armor call raises, or when the service returns anything other
than a `SUCCESS` verdict. The default blocks unscreened content. Set
`block_on_screening_failure=False` to keep the agent answering while Model Armor is
unavailable.

A blocked turn carries `custom_metadata['model_armor_blocked']`, so an application can tell a
policy block from a real answer.

## Additional resources

- [Model Armor overview](https://cloud.google.com/security-command-center/docs/model-armor-overview)
- [Create and manage templates](https://cloud.google.com/security-command-center/docs/manage-model-armor-templates)
- [Plugins](../plugins/index.md)
- [Safety and security](../safety/index.md)
- [Guardrails for live agents](../live/guardrails.md)
