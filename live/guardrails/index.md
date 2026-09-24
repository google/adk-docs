# Guardrails for live agents

Supported in ADKPython v2.8.0

Guardrails govern how live voice agents behave in production, keeping conversations on-topic, on-policy, and safe. In a live connection, audio streams continuously and the model begins speaking in real time. ADK provides multiple layers of protection that work together to secure conversations with limited impact on conversation latency.

For general callback mechanics and plugin registration, see [Types of callbacks](https://adk.dev/callbacks/types-of-callbacks/index.md) and [Plugins](https://adk.dev/plugins/index.md).

## Guardrail layers

| Layer               | What it does                                       | Protection focus          | Latency impact               |
| ------------------- | -------------------------------------------------- | ------------------------- | ---------------------------- |
| System instructions | Shapes tone, conversational rules, and boundaries  | Behavioral guidance       | No added application latency |
| Safety settings     | Enforces platform thresholds for content safety    | Platform safety filters   | No added application latency |
| Input validation    | Catches prompt injection and disallowed topics     | User input validation     | Minimal (runs per turn)      |
| Response validation | Screens agent responses against business policies  | Agent response validation | Dependent on check           |
| Tool guardrails     | Intercepts tool execution and validates parameters | Tool execution safety     | Minimal (runs per tool call) |

These layers work together to provide defense in depth. System instructions shape natural conversation flow, platform safety filters enforce baseline harm boundaries, and application validators independently verify inputs, responses, and tool calls. Combining clear instructions with independent validation ensures that if an edge case bypasses one layer, another catches it.

## Instructions and safety settings

Instructions and safety settings establish baseline behavior for the entire session. Both settings belong on the agent, which you configure when you create the session:

```python
from google.adk.agents import Agent
from google.genai import types

root_agent = Agent(
    model='gemini-live-2.5-flash-native-audio',
    name='support_agent',
    instruction=(
        'You help customers with billing questions. '
        'Never quote a price; offer to transfer to sales instead. '
        'Never discuss a competitor.'
    ),
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            ),
        ]
    ),
)
```

The model evaluates system instructions across every turn as conversation context accumulates. When designing instructions for live agents, define persona, conversational rules, and conversational guardrails in order. For strict constraints, give explicit handling rules for what to do when a boundary is hit, such as offering an alternative or transferring the caller.

Safety settings apply [safety and content filters](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/configure-safety-filters) to the live session. When the model generates content that exceeds a configured threshold, the platform terminates generation.

The live connection establishes these settings at startup, so they remain fixed for the duration of the session. An instruction string that interpolates session state renders once when the session starts, and a resumed connection reuses that rendered instruction.

## Conversation validation

Conversation validation independently evaluates what the user says and what the agent says back. For managed enterprise policies, the [Model Armor plugin](https://adk.dev/integrations/model-armor/index.md) screens prompt injection, sensitive data, and policy violations against Google Cloud templates. You can also implement custom validation using ADK model callbacks.

### User input validation

The `before_model_callback` hook intercepts user input. The callback evaluates typed text before reaching the model, so blocking prevents the message from entering context while keeping the connection open. For spoken audio, the callback inspects the transcribed utterance as a whole, only after the model has already received the audio; a block there restarts the live session to drop the reply already in flight.

When a check identifies a policy violation, returning an `LlmResponse` replaces the user's turn with a safe fallback response:

```python
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types


def block_input(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
  """Blocks a user turn that mentions a competitor."""
  text = ''.join(
      part.text or ''
      for content in llm_request.contents
      for part in content.parts or []
  )

  if 'competitor' not in text.lower():
    return None

  return LlmResponse(
      content=types.Content(
          role='model',
          parts=[types.Part(text="I can't discuss that.")],
      )
  )
```

### Agent response validation

The `after_model_callback` hook verifies model responses before or during delivery to the user. Validation can inspect the transcription as it accumulates during a spoken turn to catch violations early, or evaluate the full turn transcription.

```python
def block_output(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> Optional[LlmResponse]:
  """Replaces the response when the answer quotes a price."""
  transcription = llm_response.output_transcription
  text = transcription.text if transcription else ''

  if '$' not in text:
    return None

  return LlmResponse(
      content=types.Content(
          role='model',
          parts=[types.Part(text='Let me connect you with sales.')],
      )
  )
```

Returning an `LlmResponse` from an output callback immediately halts model generation and delivers your replacement message to the user. For spoken turns where the model already began processing the input, ADK clears the current turn so refused content does not remain in conversational context.

## Tool guardrails

Tool callbacks protect external systems and validate actions. The `before_tool_callback` hook inspects arguments before a tool executes, allowing you to reject unauthorized parameters or enforce business logic. The `after_tool_callback` hook redacts sensitive results before they return to the model:

```python
from typing import Any, Optional

from google.adk.tools import BaseTool
from google.adk.tools import ToolContext


def validate_refund(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: ToolContext,
) -> Optional[dict[str, Any]]:
  """Prevents unauthorized refunds above a threshold."""
  if tool.name == 'issue_refund' and args.get('amount', 0) > 100:
    return {'error': 'Refund exceeds automatic approval limit.'}
  return None
```

Returning a result from a tool callback bypasses tool execution and provides the return value directly to the model. See [Tool execution callbacks](https://adk.dev/callbacks/types-of-callbacks/#tool-execution-callbacks).

Live audio streams cannot pause to await interactive human confirmation. When a live agent uses tools requiring elevated privileges, validate arguments automatically within callbacks or route the request to a human handoff.

## Requirements and best practices

- **Ensure transcription remains active**: Text-based conversation validation relies on speech transcription. Both `RunConfig.input_audio_transcription` and `RunConfig.output_audio_transcription` are enabled by default. Setting either to `None` disables the corresponding screening layer.
- **Keep validators lightweight**: Callbacks in the live receive loop run inline with audio processing. Fast local checks keep the conversation responsive. For heavier checks, evaluate complete turn transcriptions or offload long-running analytics asynchronously.
- **Apply policies across agents**: Registering plugins such as [Model Armor](https://adk.dev/integrations/model-armor/index.md) on the `App` applies consistent security rules across every agent in the application without duplicating callback code.

## Additional resources

- [Model Armor plugin](https://adk.dev/integrations/model-armor/index.md)
- [Types of callbacks](https://adk.dev/callbacks/types-of-callbacks/index.md)
- [Plugins](https://adk.dev/plugins/index.md)
- [Configure safety filters](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/configure-safety-filters)
