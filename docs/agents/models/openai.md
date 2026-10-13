# OpenAI models for ADK agents

<div class="language-support-tag">
   <span class="lst-supported">Supported in ADK</span><span class="lst-go">Go v2.1.0</span><span class="lst-preview">Experimental</span>
</div>

!!! example "Experimental"

    The `openaimodel` package is experimental and its behavior may change or be removed in the future. We welcome your
		[feedback](https://github.com/google/adk-go/issues/new?template=feature_request.md)!

You can use OpenAI models with ADK. How you connect depends on the language:

- **Go — native support:** ADK Go provides a direct `openaimodel` package that implements the `model.LLM` interface, targeting the OpenAI Responses API or the [Chat Completions API](#chat-completions-api). [Get started](#get-started).
- **Python — via LiteLLM:** ADK Python accesses OpenAI models (and many other providers) through the LiteLLM connector. See [LiteLLM](/agents/models/litellm/).

## Get started

The `openaimodel` package provides a client for interacting with OpenAI's API. It implements the `model.LLM` interface and uses the OpenAI Responses API by default, or the [Chat Completions API](#chat-completions-api) when `ClientConfig.API` selects it.
The following code example shows a basic implementation for using OpenAI models in your agents:

=== "Go"

    === "Responses API"

        ```go
        import (
        	"context"
        	"log"

        	"github.com/openai/openai-go/v3"
        	"google.golang.org/adk/v2/agent/llmagent"
        	"google.golang.org/adk/v2/model/openaimodel"
        )

        // Instantiate the model
        llm, err := openaimodel.NewModel(context.Background(), openai.ChatModelGPT4oMini, &openaimodel.ClientConfig{})
        if err != nil {
          log.Fatal(err)
        }

        // Create the agent
        agent, err := llmagent.New(llmagent.Config{
          Name:        "openai_agent",
          Model:       llm,
          Instruction: "You are a helpful AI assistant.",
        })
        if err != nil {
          log.Fatal(err)
        }
        ```

        For a complete, runnable sample, see [examples/openai/responses/](https://github.com/google/adk-go/tree/main/examples/openai/responses) in the ADK Go repository.

    === "Chat Completions API"

        Requires ADK Go v2.5.0 or later.

        ```go
        import (
        	"context"
        	"log"
        	"os"

        	"github.com/openai/openai-go/v3"
        	"google.golang.org/adk/v2/agent/llmagent"
        	"google.golang.org/adk/v2/model/openaimodel"
        )

        // Instantiate the model on the Chat Completions API
        llm, err := openaimodel.NewModel(context.Background(), openai.ChatModelGPT4oMini, &openaimodel.ClientConfig{
          APIKey: os.Getenv("OPENAI_API_KEY"),
          API:    openaimodel.APIChatCompletions,
        })
        if err != nil {
          log.Fatal(err)
        }

        // Create the agent
        agent, err := llmagent.New(llmagent.Config{
          Name:        "openai_agent",
          Model:       llm,
          Instruction: "You are a helpful AI assistant.",
        })
        if err != nil {
          log.Fatal(err)
        }
        ```

        For a complete, runnable sample, see [examples/openai/completions/](https://github.com/google/adk-go/tree/main/examples/openai/completions) in the ADK Go repository.

## Chat Completions API {#chat-completions-api}

<div class="language-support-tag">
   <span class="lst-supported">Supported in ADK</span><span class="lst-go">Go v2.5.0</span><span class="lst-preview">Experimental</span>
</div>

By default, `openaimodel` sends requests to the OpenAI
[Responses API](https://platform.openai.com/docs/api-reference/responses)
(`POST /v1/responses`). Nearly every OpenAI-compatible provider implements the
[Chat Completions API](https://platform.openai.com/docs/api-reference/chat)
(`POST /v1/chat/completions`), and some implement only that one. To use it, set
the `API` field of `ClientConfig` to `openaimodel.APIChatCompletions`, as the
Chat Completions API tab under [Get started](#get-started) shows. Agents, tools,
and the runner work the same way with either API.

!!! warning "Set the API key for other providers"

    To reach another OpenAI-compatible provider, set `BaseURL` to its endpoint
    and `APIKey` to its key. When `APIKey` is empty, the `openai-go` SDK falls
    back to the `OPENAI_API_KEY` environment variable and sends that key to
    `BaseURL`.

The two APIs support the same features, with these differences:

- **Generation settings:** `StopSequences`, `FrequencyPenalty`, `PresencePenalty`, and `Seed` are sent to the Chat Completions API. The Responses API has no equivalent fields and returns an error for them.
- **Reasoning output:** The Chat Completions API does not return reasoning text, so responses contain no thought parts, and `ThinkingConfig.IncludeThoughts` is ignored. Reasoning effort and reasoning-token counts work with both APIs.
- **Output token limit:** `MaxOutputTokens` is sent as `max_completion_tokens`. Some compatible servers honor only the older `max_tokens` field, so the limit has no effect there.

## Supported features

- Text generation (streaming and non-streaming)
- Function (tool) calling
- Structured output via `OutputSchema` (JSON schema)
- Reasoning models (e.g. o-series), including reasoning-token accounting
- Token logprobs
- Tool choice via `ToolConfig.FunctionCallingConfig`: the `AUTO`, `NONE`, and `ANY` modes, with `AUTO` and `ANY` optionally limited to `AllowedFunctionNames`. Other modes, such as `VALIDATED`, return an error. The Chat Completions API receives the tool choice only when the request declares tools.
- Processing tier via `ServiceTier` (ADK Go v2.4.0 or later): `flex` and `priority` select the OpenAI tiers of the same name, and `standard` or `unspecified` selects the default tier
- Request timeout via `HTTPOptions.Timeout` (ADK Go v2.4.0 or later), which bounds the whole call, including retries and, when streaming, the full stream. ADK ignores `HTTPOptions.Headers`. To send extra headers to OpenAI, use `ClientConfig.Options`.

## Limitations

- **Text only** — multimodal input (images, audio, files) is not supported.
- **Function tools only** — built-in tools (Google Search, code execution, etc.) are not supported.
- **Structured output uses OpenAI strict mode** — every field declared in an `OutputSchema` is treated as required.
- **Function tools don't use strict mode** (ADK Go v2.5.0 or later) — ADK sends function tools with OpenAI strict schema validation off. Optional parameters stay optional, but the model's tool-call arguments might not match the declared schema. Tools built with `functiontool` validate arguments against their input schema. Other tools should validate their own input.
- **Reasoning isn't carried across turns** (ADK Go v2.5.0 or later) — ADK doesn't send reasoning from earlier turns back to the model on either API, so reasoning informs only the turn that produced it. If a later turn needs a conclusion, have the model state it in its answer.
- **Unsupported `GenerateContentConfig` settings return an error** rather than being silently ignored:
    - `TopK`, `CandidateCount` above one, `Labels`, `SafetySettings`, and a `ResponseMIMEType` other than `text/plain` or `application/json` each return their own error, such as `openaimodel.ErrTopKNotSupported` or `openaimodel.ErrUnsupportedMIMEType`.
    - The Responses API also rejects stop sequences (`ErrStopSequencesNotSupported`), frequency and presence penalties (`ErrPenaltiesNotSupported`), and seed (`ErrUnsupportedConfigField`), which the [Chat Completions API](#chat-completions-api) supports.
    - In ADK Go v2.4.0 or later, the following return `openaimodel.ErrUnsupportedConfigField`, with the setting named in the message:
        - The fields `CachedContent`, `ResponseModalities`, `MediaResolution`, `SpeechConfig`, `AudioTimestamp`, `ImageConfig`, `RoutingConfig`, `ModelSelectionConfig`, `ModelArmorConfig`, `EnableEnhancedCivicAnswers`, and `AudioTranscriptionConfig`.
        - Every `HTTPOptions` field except `Timeout` and `Headers`: `BaseURL`, `BaseURLResourceScope`, `APIVersion`, `ExtraBody`, `ExtrasRequestProvider`, and `RetryOptions`.
        - These values: an unknown `ServiceTier`, a zero or negative `HTTPOptions.Timeout`, `Logprobs` without `ResponseLogprobs`, a negative `MaxOutputTokens` or `CandidateCount`, a `ThinkingConfig.ThinkingBudget` below -1, and an unknown `ThinkingConfig.ThinkingLevel`.

## Handle incomplete and failed responses

Requires ADK Go v2.4.0 or later.

On the Responses API, when a content filter or another reason that isn't the
output token limit cuts a turn short, `FinishReason` is `SAFETY` or `OTHER`. If
the turn still returns content, `CustomMetadata[openaimodel.FinishMessageKey]`
(`"openai_finish_message"`) holds OpenAI's own reason, such as
`content_filter`. A turn cut short by `MaxOutputTokens` has `FinishReason`
`MAX_TOKENS` and no finish message. ADK's REST server doesn't include
`CustomMetadata` in events, so ADK Web shows only the `FinishReason`. On the
Chat Completions API, a content filter sets `FinishReason` to `SAFETY` with no
finish message.

A blocking call whose response has no usable output fails with
`openaimodel.ErrNoOutputItems` or `openaimodel.ErrNoTextOrToolContent` on the
Responses API, and with `openaimodel.ErrNoChoices` or
`openaimodel.ErrNoTextOrToolContent` on the Chat Completions API. When the
Responses API reports a response as failed, which arrives as HTTP 200, the
call returns an error that wraps `openaimodel.ErrResponseFailed` and includes
the response ID, error code, and message when OpenAI provides them. Check for
these errors with `errors.Is`.

## Configuration options

The `ClientConfig` provides several options for configuring the client:

- `APIKey`: Your OpenAI API key.
- `BaseURL`: Custom endpoint URL, which can be useful for OpenAI-compatible endpoints.
- `HTTPClient`: A custom `*http.Client`.
- `Options`: Advanced `openai-go` request options (`[]option.RequestOption`).
- `API`: The OpenAI API to call: `openaimodel.APIResponses` (the default) or `openaimodel.APIChatCompletions`. See [Chat Completions API](#chat-completions-api).

If `APIKey` or `BaseURL` are left empty, they will automatically fall back to the `OPENAI_API_KEY` and `OPENAI_BASE_URL` environment variables, handled by the default behavior of the underlying `openai-go` SDK.

## OpenAI model authentication

When using OpenAI models, you must provide an API key to authenticate with the OpenAI API. The most direct way to provide this information is to use environment variables or an `.env` file.

The `openaimodel` package also supports OpenAI-compatible endpoints (such as local models served via Ollama, LM Studio, or vLLM) by configuring the base URL. If the endpoint does not serve the Responses API, also set `API` to `openaimodel.APIChatCompletions`, as described in [Chat Completions API](#chat-completions-api).

=== "OpenAI API"

    ```bash
    # .env configuration file
    OPENAI_API_KEY="PASTE_YOUR_OPENAI_API_KEY_HERE"
    ```

=== "OpenAI-compatible Endpoint"

    ```bash
    # .env configuration file
    OPENAI_API_KEY="api-key-if-required"
    OPENAI_BASE_URL="http://localhost:11434/v1" # example: local Ollama endpoint
    ```
