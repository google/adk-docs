---
catalog_title: Model Armor Plugin
catalog_description: Screen user input and model output with Google Cloud Model Armor
catalog_icon: /integrations/assets/model-armor.png
catalog_tags: ["security", "google"]
---

# Model Armor plugin for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v2.8.0</span>
</div>

`ModelArmorPlugin` screens user input and model output against [Google Cloud Model Armor](https://cloud.google.com/security-command-center/docs/model-armor-overview) templates. When a filter matches, or when screening cannot complete (fail-closed by default), content is replaced with a safe message before it reaches the model or the user.

The integration provides `ModelArmorPlugin` (a `BasePlugin`) and `ModelArmorConfig` (template paths, blocked messages, `block_on_screening_failure`).

## Use cases

- **Prompt-injection / jailbreak mitigation** on inbound user text before the model call.
- **Unsafe model output blocking** before responses reach the user (unary and live transcription paths).
- **Fail-closed deployments** where unscreened content is treated as unsafe.

## Prerequisites

- Google Cloud project with [Model Armor templates](https://cloud.google.com/security-command-center/docs/manage-model-armor-templates) in a supported region (for example `us-central1`).
- `pip install 'google-adk[gcp]'` (pulls `google-cloud-modelarmor`).
- Application Default Credentials with permission to invoke Model Armor (for example `roles/modelarmor.user` on the templates).

## Installation

```shell
pip install 'google-adk[gcp]'
```

## Use with agent

```python
from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.integrations.model_armor import ModelArmorConfig
from google.adk.integrations.model_armor import ModelArmorPlugin

agent = LlmAgent(
    name="screened_agent",
    description="Assistant whose input and output are screened.",
    instruction="You are a helpful assistant.",
)

app = App(
    name="model_armor_demo",
    root_agent=agent,
    plugins=[
        ModelArmorPlugin(
            config=ModelArmorConfig(
                prompt_template_name=(
                    "projects/PROJECT_ID/locations/us-central1/templates/PROMPT_TEMPLATE"
                ),
                response_template_name=(
                    "projects/PROJECT_ID/locations/us-central1/templates/RESPONSE_TEMPLATE"
                ),
            )
        )
    ],
)
```

Prompt and response templates must use full resource paths and reside in the **same** region. The plugin targets `modelarmor.{location}.rep.googleapis.com`.

## Configuration

| Field | Description |
| --- | --- |
| `prompt_template_name` | Screen user input (`before_model_callback`). Optional. |
| `response_template_name` | Screen model output (`after_model_callback`). Optional. |
| `input_blocked_message` / `output_blocked_message` | Replacement text when blocked. |
| `block_on_screening_failure` | Default `True`: block when Model Armor cannot return SUCCESS. |

At least one template name is required.

Blocked responses include `custom_metadata['model_armor_blocked']` for UI handling.

## Limitations

- **Tool output is not screened.** The plugin reads the latest `user` content with text parts only. Tool results arrive as `function_response` parts and do not reach Model Armor. Pipelines that ingest GitHub issues, email, or web search via tools need a separate `after_tool_callback` guardrail if tool output is in scope for your threat model.
- **Regional binding:** one plugin instance maps to one Model Armor region; prompt and response templates must match.
- **Live audio** is screened via transcriptions, not raw audio.

For plugin architecture background, see [Plugins](/plugins/) and [Safety guardrails](/safety/).

## Resources

- [Model Armor overview](https://cloud.google.com/security-command-center/docs/model-armor-overview)
- [Manage Model Armor templates](https://cloud.google.com/security-command-center/docs/manage-model-armor-templates)
- [adk-python source guide](https://github.com/google/adk-python/blob/main/docs/guides/integrations/model_armor/index.md)
