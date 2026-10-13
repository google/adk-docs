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
- Tool choice via `ToolConfig.FunctionCallingConfig`: the `AUTO`, `NONE`, and `ANY` modes, optionally limited to `AllowedFunctionNames`
- Processing tier via `ServiceTier`: `flex` and `priority` select the OpenAI tiers of the same name, and `standard` selects the default tier
- Request timeout via `HTTPOptions.Timeout`, which bounds the whole call, including retries and, when streaming, the full stream. `HTTPOptions.Headers` is ignored. To send extra headers to OpenAI, use `ClientConfig.Options`.

## Limitations

- **Text only** — multimodal input (images, audio, files) is not supported.
- **Function tools only** — built-in tools (Google Search, code execution, etc.) are not supported.
- **Structured output uses OpenAI strict mode** — every field declared in an `OutputSchema` is treated as required.
- **Function tools don't use strict mode** — tools are sent with OpenAI strict schema validation off, so optional parameters stay optional, but tool-call arguments aren't guaranteed to match the declared schema. Tools built with `functiontool` validate arguments against their input schema. Other tools should validate their own input.
- **Reasoning isn't carried across turns** — reasoning from earlier turns isn't sent back to the model on either API, so it informs only the turn that produced it. If a later turn needs a conclusion, have the model state it in its answer.
- **Unsupported `GenerateContentConfig` fields return an error** rather than being silently ignored:
    - `TopK`, `CandidateCount` above one, `Labels`, `SafetySettings`, and a `ResponseMIMEType` other than `text/plain` or `application/json` each return their own error, such as `openaimodel.ErrTopKNotSupported`.
    - `CachedContent`, `ResponseModalities`, `MediaResolution`, `SpeechConfig`, `AudioTimestamp`, `ImageConfig`, `RoutingConfig`, `ModelSelectionConfig`, `ModelArmorConfig`, `EnableEnhancedCivicAnswers`, `AudioTranscriptionConfig`, and every `HTTPOptions` field except `Timeout` and `Headers` (`BaseURL`, `BaseURLResourceScope`, `APIVersion`, `ExtraBody`, `ExtrasRequestProvider`, and `RetryOptions`) return `openaimodel.ErrUnsupportedConfigField`, with the field name in the message. So do an unknown `ServiceTier` and a zero or negative `HTTPOptions.Timeout`.
    - The Responses API also rejects stop sequences, frequency/presence penalties, and seed, which the [Chat Completions API](#chat-completions-api) supports.

## Incomplete and failed responses

On the Responses API, when a turn is cut short but still returns content, for example by a content filter, `FinishReason` is `SAFETY` or `OTHER`, and `CustomMetadata[openaimodel.FinishMessageKey]` (`"openai_finish_message"`) holds OpenAI's own reason, such as `content_filter`. A turn with no content reports `SAFETY` or `OTHER` in `ErrorCode` and OpenAI's reason in `ErrorMessage` instead. ADK's REST server doesn't include `CustomMetadata` in events, so ADK Web shows only the `FinishReason`. On the Chat Completions API, a content filter sets `FinishReason` to `SAFETY` with no further metadata.

When the Responses API reports a response as failed, which arrives as HTTP 200, the model returns an error that wraps `openaimodel.ErrResponseFailed` and includes the response ID, error code, and message when OpenAI provides them. Check for it with `errors.Is`.

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
